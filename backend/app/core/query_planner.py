"""
Adaptive Query Planner — Intent detection + execution plan.

Uses a fast rule-based classifier (< 1ms) as the primary method.
Optionally calls Ollama for ambiguous queries if PLANNER_USE_LLM=True and
a fast-enough model is available.

Falls back to the full pipeline if anything fails.
"""

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Execution Plan Schema ─────────────────────────────────────────────────────


@dataclass
class ExecutionPlan:
    """Structured output from the query planner."""
    intent: str = "general"           # e.g. "factual_lookup", "comparison", "policy_lookup", "multi_hop"
    complexity: str = "medium"        # "simple", "medium", "complex"
    steps: List[str] = field(default_factory=lambda: [
        "query_expansion", "hybrid_search", "rerank", "generate_answer"
    ])
    reasoning: str = ""               # short explanation from the planner

    @property
    def skip_query_expansion(self) -> bool:
        return "query_expansion" not in self.steps

    @property
    def needs_multi_hop(self) -> bool:
        return "multi_hop_retrieval" in self.steps


# ── Default Plans ─────────────────────────────────────────────────────────────

FULL_PLAN = ExecutionPlan(
    intent="unknown",
    complexity="medium",
    steps=["query_expansion", "hybrid_search", "rerank", "generate_answer"],
    reasoning="default: running full pipeline",
)

SIMPLE_PLAN = ExecutionPlan(
    intent="simple_lookup",
    complexity="simple",
    steps=["hybrid_search", "rerank", "generate_answer"],
    reasoning="simple query: skipping query expansion",
)

COMPLEX_PLAN = ExecutionPlan(
    intent="complex_analysis",
    complexity="complex",
    steps=["query_expansion", "hybrid_search", "rerank", "generate_answer"],
    reasoning="complex query: full pipeline with expansion",
)


# ── Plan Cache (in-memory, keyed by normalized query) ─────────────────────────

_plan_cache: Dict[str, tuple] = {}  # key → (plan, timestamp)


def _cache_key(query: str) -> str:
    normalized = query.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def _get_cached_plan(query: str) -> Optional[ExecutionPlan]:
    key = _cache_key(query)
    if key in _plan_cache:
        plan, ts = _plan_cache[key]
        if time.time() - ts < settings.PLANNER_CACHE_TTL:
            return plan
        del _plan_cache[key]
    return None


def _set_cached_plan(query: str, plan: ExecutionPlan):
    key = _cache_key(query)
    if len(_plan_cache) > 2000:
        oldest_key = next(iter(_plan_cache))
        del _plan_cache[oldest_key]
    _plan_cache[key] = (plan, time.time())


# ── Rule-Based Classifier (< 1ms) ────────────────────────────────────────────

# Patterns that indicate SIMPLE queries (skip expansion)
_SIMPLE_STARTERS = [
    "what is", "what are", "what was", "what were",
    "who is", "who are", "who was",
    "when is", "when was", "when did",
    "where is", "where are", "where was",
    "how many", "how much", "how long",
    "define", "meaning of", "definition of",
    "is there", "are there", "does it", "do they",
]

# Patterns that indicate COMPLEX queries (need expansion)
_COMPLEX_PATTERNS = [
    "compare", "contrast", "difference between", "differences between",
    "versus", " vs ", " vs. ",
    "step by step", "step-by-step",
    "explain how", "explain why", "explain the",
    "analyze", "evaluate", "assess",
    "pros and cons", "advantages and disadvantages",
    "relationship between", "correlation between",
    "impact of", "effect of", "effects of",
    "how does .* affect", "how does .* impact",
    "what are the .* and .*",
    "list all", "enumerate", "summarize all",
    "what factors", "what causes",
]

# Compiled regex for complex patterns (avoids recompiling each call)
_COMPLEX_REGEX = re.compile("|".join(_COMPLEX_PATTERNS), re.IGNORECASE)


def _classify_query(query: str) -> str:
    """
    Rule-based query complexity classifier.
    Returns: "simple", "medium", or "complex"
    Runs in < 1ms.
    """
    q = query.lower().strip()
    words = q.split()
    word_count = len(words)

    # ── Very short queries are almost always simple ──
    if word_count <= 4:
        return "simple"

    # ── Check for complex patterns ──
    if _COMPLEX_REGEX.search(q):
        return "complex"

    # ── Check for simple starters ──
    for starter in _SIMPLE_STARTERS:
        if q.startswith(starter):
            # But if it's long (> 12 words), it might be complex despite simple starter
            if word_count > 12:
                return "medium"
            return "simple"

    # ── Questions with "?" that are short tend to be simple ──
    if q.endswith("?") and word_count <= 8:
        return "simple"

    # ── Multi-sentence or very long queries are complex ──
    sentence_count = len([s for s in re.split(r'[.!?]', q) if s.strip()])
    if sentence_count >= 3 or word_count > 20:
        return "complex"

    # ── Default: medium complexity ──
    return "medium"


def _detect_intent(query: str) -> str:
    """Lightweight intent classification based on keywords."""
    q = query.lower()

    if any(w in q for w in ["policy", "rule", "guideline", "regulation", "requirement"]):
        return "policy_lookup"
    if any(w in q for w in ["compare", "versus", "vs", "difference", "better"]):
        return "comparison"
    if any(w in q for w in ["how to", "steps", "process", "procedure", "guide"]):
        return "how_to"
    if any(w in q for w in ["why", "reason", "cause", "explain"]):
        return "explanation"
    if any(w in q for w in ["list", "all", "enumerate", "what are the"]):
        return "enumeration"
    if any(w in q for w in ["define", "what is", "meaning", "definition"]):
        return "definition"

    return "general"


def _build_plan(query: str) -> ExecutionPlan:
    """Build an execution plan from rule-based classification."""
    complexity = _classify_query(query)
    intent = _detect_intent(query)

    if complexity == "simple":
        return ExecutionPlan(
            intent=intent,
            complexity="simple",
            steps=["hybrid_search", "rerank", "generate_answer"],
            reasoning="simple query: skipping query expansion to save latency",
        )
    elif complexity == "complex":
        return ExecutionPlan(
            intent=intent,
            complexity="complex",
            steps=["query_expansion", "hybrid_search", "rerank", "generate_answer"],
            reasoning="complex query: using query expansion for better coverage",
        )
    else:  # medium
        return ExecutionPlan(
            intent=intent,
            complexity="medium",
            steps=["query_expansion", "hybrid_search", "rerank", "generate_answer"],
            reasoning="medium complexity: using full pipeline",
        )


# ── Ollama Client (optional, for users with fast hardware) ────────────────────

PLANNER_SYSTEM_PROMPT = """You are a query analysis engine. Analyze the user query and return a JSON execution plan.

Rules:
- "simple" queries: short, direct factual lookups → skip query_expansion
- "medium" queries: need some context or comparison → include query_expansion
- "complex" queries: multi-part, reasoning-heavy → include query_expansion

Available steps (use only these):
- query_expansion: generates alternative search queries (skip for simple queries)
- hybrid_search: vector + keyword search (always required)
- rerank: reorder results by relevance (always recommended)
- generate_answer: LLM answer generation (always required)

Return ONLY valid JSON, no markdown:
{"intent": "<intent>", "complexity": "<simple|medium|complex>", "steps": [...], "reasoning": "<1 sentence>"}"""


async def _call_ollama(query: str) -> Optional[dict]:
    """Call local Ollama — only used if PLANNER_USE_LLM is enabled."""
    url = f"{settings.PLANNER_OLLAMA_URL.rstrip('/')}/api/generate"
    payload = {
        "model": settings.PLANNER_MODEL,
        "prompt": f"Analyze this query and return a JSON execution plan:\n\n\"{query}\"",
        "system": PLANNER_SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 150,
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=settings.PLANNER_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            return _parse_plan_json(data.get("response", ""))
    except httpx.TimeoutException:
        logger.warning(f"[Planner] Ollama timed out after {settings.PLANNER_TIMEOUT}s")
        return None
    except Exception as e:
        logger.warning(f"[Planner] Ollama failed: {e}")
        return None


def _parse_plan_json(text: str) -> Optional[dict]:
    """Extract JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict) or "steps" not in parsed:
            return None
        valid_steps = {"query_expansion", "hybrid_search", "rerank", "generate_answer"}
        parsed["steps"] = [s for s in parsed["steps"] if s in valid_steps]
        if "hybrid_search" not in parsed["steps"]:
            parsed["steps"].insert(0, "hybrid_search")
        if "generate_answer" not in parsed["steps"]:
            parsed["steps"].append("generate_answer")
        return parsed
    except (json.JSONDecodeError, TypeError):
        return None


# ── Public API ────────────────────────────────────────────────────────────────

async def plan_query(query: str) -> ExecutionPlan:
    """
    Analyze a query and return an adaptive execution plan.

    Strategy:
    1. Check plan cache → return immediately if hit
    2. Rule-based classifier (< 1ms) → primary method
    3. Optionally call Ollama for medium queries if PLANNER_USE_LLM=True
    4. Fallback to full pipeline on any failure
    """
    if not settings.PLANNER_ENABLED:
        return FULL_PLAN

    # 1. Cache check
    cached = _get_cached_plan(query)
    if cached:
        logger.info(f"[Planner] Cache hit — intent={cached.intent}, complexity={cached.complexity}")
        return cached

    t0 = time.time()

    # 2. Rule-based classification (always runs, < 1ms)
    plan = _build_plan(query)
    elapsed = time.time() - t0
    logger.info(
        f"[Planner] Classified → intent={plan.intent}, "
        f"complexity={plan.complexity}, skip_expansion={plan.skip_query_expansion} ({elapsed:.4f}s)"
    )

    _set_cached_plan(query, plan)
    return plan
