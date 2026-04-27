"""
Model Registry — Central registry for all supported LLM providers.
Each provider uses OpenAI-compatible API format with different base URLs.
"""

from dataclasses import dataclass
from typing import Optional
from langchain_openai import ChatOpenAI
from app.core.config import settings


@dataclass
class ModelInfo:
    """Metadata for a supported model."""
    id: str                 # unique key, e.g. "openai/gpt-3.5-turbo"
    name: str               # display name
    provider: str           # "openai", "sarvam", "groq"
    model_name: str         # actual model name to pass to API
    base_url: Optional[str] # None = default OpenAI, else custom endpoint
    api_key_env: str        # which settings attr holds the key
    description: str        # shown in UI
    context_window: int     # tokens
    cost_tier: str          # "free", "cheap", "moderate", "expensive"


# ── Model Catalog ────────────────────────────────────────────

MODELS: dict[str, ModelInfo] = {
    # ── OpenAI ──
    "gpt-3.5-turbo": ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider="openai",
        model_name="gpt-3.5-turbo-0125",
        base_url=None,
        api_key_env="OPENAI_API_KEY",
        description="Fast & cheap. Great for most RAG tasks.",
        context_window=16385,
        cost_tier="cheap",
    ),
    "gpt-4-turbo": ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider="openai",
        model_name="gpt-4-turbo",
        base_url=None,
        api_key_env="OPENAI_API_KEY",
        description="Most capable. Best for complex reasoning.",
        context_window=128000,
        cost_tier="expensive",
    ),
    "gpt-4o-mini": ModelInfo(
        id="gpt-4o-mini",
        name="GPT-4o Mini",
        provider="openai",
        model_name="gpt-4o-mini",
        base_url=None,
        api_key_env="OPENAI_API_KEY",
        description="Balanced speed & quality. Good default.",
        context_window=128000,
        cost_tier="moderate",
    ),

    # ── Sarvam AI (Mistral-based, Indian language optimized) ──
    "sarvam-m": ModelInfo(
        id="sarvam-m",
        name="Sarvam-M",
        provider="sarvam",
        model_name="sarvam-m",
        base_url="https://api.sarvam.ai/v1",
        api_key_env="SARVAM_API_KEY",
        description="Multilingual (Indian languages). Hybrid reasoning.",
        context_window=32000,
        cost_tier="cheap",
    ),

    # ── Groq (Ultra-fast inference) ──
    "groq-llama-3.3-70b": ModelInfo(
        id="groq-llama-3.3-70b",
        name="Llama 3.3 70B (Groq)",
        provider="groq",
        model_name="llama-3.3-70b-versatile",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        description="Powerful Llama 3.3 70B. Blazing fast via Groq LPU.",
        context_window=8192,
        cost_tier="free",
    ),
    "groq-llama-3.1-8b": ModelInfo(
        id="groq-llama-3.1-8b",
        name="Llama 3.1 8B (Groq)",
        provider="groq",
        model_name="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        description="Fast, open-source Llama 3.1 8B. Great for RAG.",
        context_window=8192,
        cost_tier="free",
    ),

    "groq-mixtral-8x7b": ModelInfo(
        id="groq-mixtral-8x7b",
        name="Mixtral 8x7B (Groq)",
        provider="groq",
        model_name="mixtral-8x7b-32768",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        description="Strong MoE model with 32K context. Great RAG value.",
        context_window=32768,
        cost_tier="free",
    ),

    # ── ZhipuAI (GLM) ──
    "glm-4": ModelInfo(
        id="glm-4",
        name="GLM-4",
        provider="zhipu",
        model_name="glm-4",
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        api_key_env="ZHIPUAI_API_KEY",
        description="ZhipuAI's flagship model. Comparable to GPT-4.",
        context_window=128000,
        cost_tier="moderate",
    ),
    "glm-4-flash": ModelInfo(
        id="glm-4-flash",
        name="GLM-4 Flash",
        provider="zhipu",
        model_name="glm-4-flash",
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        api_key_env="ZHIPUAI_API_KEY",
        description="High speed, low cost. Good for simple queries.",
        context_window=128000,
        cost_tier="cheap",
    ),
    "glm-5": ModelInfo(
        id="glm-5",
        name="GLM-5 (Beta)",
        provider="zhipu",
        model_name="glm-5", # Verify exact model string if available, usually consistent
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        api_key_env="ZHIPUAI_API_KEY",
        description="Next-gen 744B param model. State of the art.",
        context_window=128000, # Assuming similar context
        cost_tier="expensive",
    ),

    # ── DeepSeek ──
    "deepseek-chat": ModelInfo(
        id="deepseek-chat",
        name="DeepSeek V3",
        provider="deepseek",
        model_name="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
        description="DeepSeek V3. Excellent general purpose chat model.",
        context_window=64000,
        cost_tier="cheap",
    ),
    "deepseek-reasoner": ModelInfo(
        id="deepseek-reasoner",
        name="DeepSeek R1 (Reasoner)",
        provider="deepseek",
        model_name="deepseek-reasoner",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
        description="Reasoning model. Thinks before answering (CoT).",
        context_window=64000,
        cost_tier="moderate",
    ),

    # ── Google Gemini (native via google-genai) ──
    "gemini-2.5-flash": ModelInfo(
        id="gemini-2.5-flash",
        name="Gemini 2.5 Flash",
        provider="gemini",
        model_name="gemini-2.5-flash",
        base_url=None,
        api_key_env="GEMINI_API_KEY",
        description="Fast Gemini model. Good for low-latency RAG.",
        context_window=1000000,
        cost_tier="moderate",
    ),
    "gemini-2.5-pro": ModelInfo(
        id="gemini-2.5-pro",
        name="Gemini 2.5 Pro",
        provider="gemini",
        model_name="gemini-2.5-pro",
        base_url=None,
        api_key_env="GEMINI_API_KEY",
        description="Most capable Gemini model. Best for complex reasoning.",
        context_window=2000000,
        cost_tier="expensive",
    ),
}


# Backward-compatible aliases (old UI/model ids)
MODEL_ALIASES: dict[str, str] = {
    "groq-llama3": "groq-llama-3.3-70b",
    "groq-mixtral": "groq-mixtral-8x7b",
}


def resolve_model_id(model_id: str) -> str:
    """Map legacy model ids to current ids."""
    return MODEL_ALIASES.get(model_id, model_id)


def get_available_models() -> list[dict]:
    """Return models that have valid API keys configured."""
    available = []
    for model_id, info in MODELS.items():
        api_key = getattr(settings, info.api_key_env, "")
        available.append({
            "id": info.id,
            "name": info.name,
            "provider": info.provider,
            "description": info.description,
            "context_window": info.context_window,
            "cost_tier": info.cost_tier,
            "available": bool(api_key),  # True if API key is set
        })
    return available


def get_llm_for_model(model_id: str, temperature: float = 0.0) -> ChatOpenAI:
    """
    Create a LangChain ChatOpenAI instance for the given model.
    Works with any OpenAI-compatible provider (Sarvam, Groq, etc).
    """
    model_id = resolve_model_id(model_id)
    info = MODELS.get(model_id)
    if not info:
        # Fallback to GPT-3.5-turbo
        info = MODELS["gpt-3.5-turbo"]

    api_key = getattr(settings, info.api_key_env, "") or settings.OPENAI_API_KEY

    kwargs = {
        "model": info.model_name,
        "temperature": temperature,
        "api_key": api_key,
    }

    if info.base_url:
        kwargs["base_url"] = info.base_url

    return ChatOpenAI(**kwargs)
