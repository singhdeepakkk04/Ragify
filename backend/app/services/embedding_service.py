from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol
import os, asyncio, logging

logger = logging.getLogger(__name__)

class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

# ── Abstract base ──────────────────────────────────────────────────────────
class BaseEmbeddingService(ABC):
    
    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embed a user query (uses task:retrieval_query instruction)"""
        ...
    
    @abstractmethod  
    async def embed_document(self, text: str) -> list[float]:
        """Embed a document chunk (uses task:retrieval_document instruction)"""
        ...
    
    @abstractmethod
    async def embed_documents_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple document chunks efficiently"""
        ...
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimension this provider produces"""
        ...
    
    @property
    @abstractmethod
    def provider_name(self) -> EmbeddingProvider:
        ...

# ── OpenAI implementation (preserve existing logic) ────────────────────────
class OpenAIEmbeddingService(BaseEmbeddingService):
    """
    Existing OpenAI embedding logic moved here unchanged.
    Model: text-embedding-3-small (1536-dim) by default.
    Reads OPENAI_API_KEY from env.
    """
    
    def __init__(self, model: str = "text-embedding-3-small"):
        # Keep exactly whatever setup code existed before
        # Just wrap it in this class
        import openai
        from app.core.config import settings
        # Using settings instead of os.environ to keep consistency with app
        self._client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model

    async def embed_query(self, text: str) -> list[float]:
        # Existing OpenAI embed logic
        response = await self._client.embeddings.create(
            model=self._model, input=text
        )
        return response.data[0].embedding

    async def embed_document(self, text: str) -> list[float]:
        # Same call — OpenAI doesn't differentiate query vs doc
        return await self.embed_query(text)

    async def embed_documents_batch(self, texts: list[str]) -> list[list[float]]:
        response = await self._client.embeddings.create(
            model=self._model, input=texts
        )
        return [d.embedding for d in response.data]

    @property
    def dimension(self) -> int:
        return 1536  # text-embedding-3-small

    @property
    def provider_name(self) -> EmbeddingProvider:
        return EmbeddingProvider.OPENAI

# ── Gemini implementation ──────────────────────────────────────────────────
class GeminiEmbeddingService(BaseEmbeddingService):
    """
    Google Gemini Embedding 2 (gemini-embedding-2-preview).
    Uses 768-dim Matryoshka truncation — same quality, 75% less storage vs 3072-dim.
    Reads GEMINI_API_KEY from env.
    
    Key difference from OpenAI: task instructions matter for quality.
    - Queries use "task:retrieval_query" prefix
    - Documents use "task:retrieval_document" prefix
    """
    
    _semaphore = asyncio.Semaphore(20)  # respect Gemini rate limits
    
    def __init__(self):
        import google.genai as genai
        from app.core.config import settings
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = "gemini-embedding-2-preview"

    async def _embed(self, text: str) -> list[float]:
        async with self._semaphore:
            response = await asyncio.to_thread(
                self._client.models.embed_content,
                model=self._model,
                contents=text,
                config={"output_dimensionality": 768},
            )
            return response.embeddings[0].values

    async def embed_query(self, text: str) -> list[float]:
        return await self._embed(f"task:retrieval_query {text}")

    async def embed_document(self, text: str) -> list[float]:
        return await self._embed(f"task:retrieval_document {text}")

    async def embed_documents_batch(self, texts: list[str]) -> list[list[float]]:
        # Gemini doesn't have a batch endpoint — parallelise with gather
        tasks = [self.embed_document(t) for t in texts]
        return await asyncio.gather(*tasks)

    @property
    def dimension(self) -> int:
        return 768

    @property
    def provider_name(self) -> EmbeddingProvider:
        return EmbeddingProvider.GEMINI

# ── Factory ────────────────────────────────────────────────────────────────
def get_embedding_service(provider: str) -> BaseEmbeddingService:
    """
    Call this wherever you need an embedding service.
    Pass project.embedding_provider to get the right one.
    
    Usage:
        svc = get_embedding_service(project.embedding_provider)
        vector = await svc.embed_query(user_query)
    """
    if provider == EmbeddingProvider.GEMINI:
        return GeminiEmbeddingService()
    return OpenAIEmbeddingService()  # default — preserves all existing behaviour
