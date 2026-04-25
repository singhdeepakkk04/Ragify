"""
Langfuse Tracing Module for RAGify

Provides a singleton Langfuse client + helpers to instrument the RAG pipeline.
All traces are sent asynchronously so there is zero blocking latency added to
the hot query path.

Usage:
    from app.core.tracing import get_langfuse, observe_span

    lf = get_langfuse()
    trace = lf.trace(name="query_project", user_id=str(user_id))
    
    span = trace.span(name="embed_query")
    # ... do work ...
    span.end()

If LANGFUSE_SECRET_KEY is not set, all calls become no-ops so the app works
without Langfuse configured (dev mode / testing).
"""

import logging
import time
from contextlib import contextmanager
from typing import Optional, Any, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)

_langfuse_client = None
_langfuse_available = False


def get_langfuse():
    """
    Returns the Langfuse singleton, or a NullLangfuse stub if not configured.
    Call once at app startup or lazily on first use.
    """
    global _langfuse_client, _langfuse_available

    if _langfuse_client is not None:
        return _langfuse_client

    secret_key = getattr(settings, "LANGFUSE_SECRET_KEY", None)
    public_key = getattr(settings, "LANGFUSE_PUBLIC_KEY", None)
    host = getattr(settings, "LANGFUSE_HOST", "http://localhost:3001")

    if not secret_key or not public_key:
        logger.info(
            "[Tracing] LANGFUSE_SECRET_KEY / LANGFUSE_PUBLIC_KEY not set — "
            "tracing is disabled (NullLangfuse active)"
        )
        _langfuse_client = NullLangfuse()
        return _langfuse_client

    try:
        from langfuse import Langfuse
        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            # Flush traces in the background — no blocking on hot path
            flush_at=5,
            flush_interval=1.0,
        )
        _langfuse_available = True
        logger.info(f"[Tracing] Langfuse connected → {host}")
    except Exception as e:
        logger.warning(f"[Tracing] Langfuse init failed: {e} — tracing disabled")
        _langfuse_client = NullLangfuse()

    return _langfuse_client


# ── Null Object Pattern (no-op when Langfuse not configured) ──────────────────

class NullSpan:
    def end(self, **kwargs): pass
    def update(self, **kwargs): pass
    def generation(self, **kwargs): return NullSpan()
    def span(self, **kwargs): return NullSpan()
    def score(self, **kwargs): pass


class NullTrace:
    def span(self, **kwargs): return NullSpan()
    def generation(self, **kwargs): return NullSpan()
    def update(self, **kwargs): pass
    def score(self, **kwargs): pass


class NullLangfuse:
    def trace(self, **kwargs): return NullTrace()
    def flush(self): pass


# ── Convenience context manager ───────────────────────────────────────────────

@contextmanager
def timed_span(parent, name: str, input_data: Optional[Dict] = None):
    """
    Context manager that creates a Langfuse span, records timing,
    and ends it automatically. Yields the span for metadata updates.
    
    Usage:
        with timed_span(trace, "embed_query", {"query": query}) as span:
            result = await embed_query(query)
            span.update(output={"embedding_dim": len(result)})
    """
    t0 = time.time()
    span = parent.span(name=name, input=input_data or {})
    try:
        yield span
    finally:
        latency_ms = round((time.time() - t0) * 1000, 2)
        span.update(metadata={"latency_ms": latency_ms})
        span.end()
        logger.debug(f"[Trace] {name}: {latency_ms}ms")
