import asyncio
import logging
from dataclasses import dataclass
from typing import Literal

from app.models.project import Project

logger = logging.getLogger(__name__)

@dataclass
class QueryPlan:
    tier: Literal["fast", "balanced", "thorough"]
    run_query_expansion: bool
    run_reranking: bool
    run_web_search: bool
    top_k_retrieval: int
    reasoning: str

_classifier_semaphore = asyncio.Semaphore(10)

async def _classify_query_groq(query: str) -> str:
    """Use Groq (Llama 3) to classify query complexity."""
    from app.core.config import settings
    
    if not settings.GROQ_API_KEY:
        logger.warning("[Query Planner] GROQ_API_KEY not set. Defaulting to 'balanced'.")
        return "balanced"

    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        timeout=2.0
    )

    prompt = f"""You are a query complexity classifier. Respond with ONLY one word.
    
    Rules:
    - "fast": greetings, simple factual lookups, yes/no questions, short definitions
    - "balanced": explanations, multi-part questions, how-to queries  
    - "thorough": research questions, legal/financial/medical queries, 
                  questions requiring synthesis across multiple sources,
                  anything containing words like "compare", "analyse", "all", "every", 
                  "regulations", "rules", "law", "policy"
    
    Query: {query}
    Classification:"""

    try:
        async with _classifier_semaphore:
            response = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.0
            )
            val = response.choices[0].message.content.strip().lower()
            if val in ("fast", "balanced", "thorough"):
                return val
            return "balanced"
    except asyncio.TimeoutError:
        logger.warning("[Query Planner] Groq classification timed out. Defaulting to 'balanced'.")
        return "balanced"
    except Exception as e:
        logger.error(f"[Query Planner] Groq classification failed: {e}. Defaulting to 'balanced'.")
        return "balanced"

async def plan_query(query: str, project: Project) -> QueryPlan:
    tier = ""
    reasoning = ""
    
    if getattr(project, "allow_errors", False):
        tier = "fast"
        reasoning = "project explicitly allows errors (max speed)"
    elif getattr(project, "retrieval_strategy", "balanced") == "fast":
        tier = "fast"
        reasoning = "project configured for 'fast' strategy"
    elif getattr(project, "retrieval_strategy", "balanced") == "thorough":
        tier = "thorough"
        reasoning = "project configured for 'thorough' strategy"
    else:
        tier = await _classify_query_groq(query)
        reasoning = "classified by groq-llama-3.1-8b"

    # Default logic limits web search to "thorough" tier or if explicitly preferred, 
    # but the prompt says tier specifies it via "thorough=expansion+rerank+web", 
    # yet there are checks for query plan "run_web_search". I'll enable it 
    # only for thorough AND project pref.
    enable_web = getattr(project, "enable_web_search", False)

    if tier == "fast":
        return QueryPlan("fast", False, False, False, 5, reasoning)
    elif tier == "balanced":
        return QueryPlan("balanced", False, True, False, 10, reasoning)
    else:
        return QueryPlan("thorough", True, True, enable_web, 15, reasoning)
