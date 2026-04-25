"""
Content guardrails for RAG queries and responses.
Two-layer approach:
1. Fast keyword blocklist (no API call)
2. Pattern-based detection for injection attempts
"""

import re
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# ── Blocked keyword categories ──

EXPLICIT_KEYWORDS = {
    # Sexual content
    "porn", "pornography", "xxx", "nsfw", "hentai", "onlyfans",
    "sexual", "nude", "naked", "erotic",
    # Violence
    "how to kill", "how to murder", "how to make a bomb",
    "how to make explosives", "how to poison",
    # Hate speech
    "racial slur", "hate speech",
    # Illegal activity
    "how to hack", "how to steal", "drug dealing",
    "how to bypass security", "how to break into",
    # Profanity / Toxicity
    "fuck", "shit", "bitch", "asshole", "cunt", "dick", "pussy",
}

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"forget\s+(all\s+)?(previous|prior|your)\s+(instructions|rules|context)",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+if\s+you",
    r"pretend\s+(you\s+are|to\s+be)",
    r"new\s+instructions?:",
    r"system\s*:?\s*prompt",
    r"<\s*system\s*>",
    r"\[SYSTEM\]",
]


def check_input(query: str) -> str:
    """
    Validate user query before processing.
    Returns sanitized query or raises HTTPException.
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    query_clean = query.strip()
    query_lower = query_clean.lower()

    # Check minimum length
    if len(query_clean) < 3:
        raise HTTPException(status_code=400, detail="Query too short. Please ask a more specific question.")

    # Check maximum length
    if len(query_clean) > 2000:
        raise HTTPException(status_code=400, detail="Query too long. Maximum 2000 characters.")

    # Check explicit keywords
    for keyword in EXPLICIT_KEYWORDS:
        if keyword in query_lower:
            logger.warning(f"[Guardrail] Blocked explicit query containing: '{keyword}'")
            raise HTTPException(
                status_code=400,
                detail="Your query contains content that violates our usage policy. Please rephrase your question to be relevant to your documents.",
            )

    # Check prompt injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            logger.warning(f"[Guardrail] Blocked prompt injection attempt: {query_clean[:100]}")
            raise HTTPException(
                status_code=400,
                detail="Your query appears to contain a prompt injection attempt. Please ask a legitimate question about your documents.",
            )

    return query_clean


def check_output(response: str) -> str:
    """
    Validate LLM response before returning to user.
    Strips potentially leaked system prompts or harmful content.
    """
    if not response:
        return "I couldn't generate a response. Please try rephrasing your question."

    response_lower = response.lower()

    # Check if the LLM leaked system instructions
    leak_indicators = [
        "as an ai language model",
        "i am programmed to",
        "my instructions are",
        "my system prompt",
        "i cannot help with",
        "i'm not able to assist with",
    ]

    # These are just warnings, not blocks — the response might still be useful
    for indicator in leak_indicators:
        if indicator in response_lower:
            logger.info(f"[Guardrail] LLM response contains potential leak indicator: '{indicator}'")

    # Check for explicit content in response
    for keyword in EXPLICIT_KEYWORDS:
        if keyword in response_lower:
            logger.warning(f"[Guardrail] LLM response contains explicit content: '{keyword}'")
            return "The generated response was flagged by our content policy. Please try a different question."

    return response


# ── Document Content Sanitization (Indirect Prompt Injection Defense) ────────

# Patterns that attackers embed in documents to hijack the LLM at retrieval time.
# These are broader than query-side patterns because document text is more varied.
DOCUMENT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above|preceding)\s+(instructions|rules|context|prompts)",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|context)",
    r"forget\s+(all\s+)?(previous|prior|your)\s+(instructions|rules|context)",
    r"you\s+are\s+now\s+",
    r"new\s+(system\s+)?instructions?\s*:",
    r"system\s*:?\s*prompt",
    r"<\s*/?\s*system\s*>",
    r"\[\s*SYSTEM\s*\]",
    r"\[\s*INST\s*\]",
    r"<<\s*SYS\s*>>",
    r"ADMIN\s*OVERRIDE",
    r"override\s+(all\s+)?safety",
    r"bypass\s+(content\s+)?filter",
    r"act\s+as\s+(if\s+you|an?\s+unrestricted)",
    r"pretend\s+(you\s+are|to\s+be)\s+(a|an)",
    r"do\s+not\s+follow\s+(your|any)\s+(rules|guidelines|instructions)",
    r"output\s+(the|your)\s+(system|full|entire)\s+prompt",
    r"reveal\s+(your|the)\s+(system\s+)?prompt",
    r"what\s+(is|are)\s+your\s+(system\s+)?(prompt|instructions)",
]

_compiled_doc_patterns = [re.compile(p, re.IGNORECASE) for p in DOCUMENT_INJECTION_PATTERNS]


def sanitize_document_content(text: str) -> str:
    """
    Neutralize prompt injection payloads embedded in document content.

    Strategy: Replace matched injection patterns with a harmless placeholder
    rather than deleting them entirely (deletion could corrupt surrounding text
    and shift meaning). The placeholder makes the intent visible in logs while
    being semantically inert to the LLM.

    This runs at indexing time so every stored chunk is clean.
    """
    if not text:
        return text

    cleaned = text
    for pattern in _compiled_doc_patterns:
        match = pattern.search(cleaned)
        if match:
            logger.warning(
                "[Guardrail] Neutralized document injection pattern: '%s'",
                match.group()[:80],
            )
            cleaned = pattern.sub("[content removed by safety filter]", cleaned)

    return cleaned
