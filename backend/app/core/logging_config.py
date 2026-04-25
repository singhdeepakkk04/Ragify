"""
Structured logging middleware — adds request_id to every log line
and logs request/response metadata in JSON format.
"""

import logging
import time
import uuid
import json
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Context variable so any logger in the call stack can access the request_id
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Inject request_id into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get("-")
        return True


class StructuredLogMiddleware(BaseHTTPMiddleware):
    """Log every request with timing, status, and a unique request ID."""

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request_id_ctx.set(rid)
        request.state.request_id = rid

        t0 = time.time()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = round((time.time() - t0) * 1000, 1)
            status = response.status_code if response else 500
            logger = logging.getLogger("ragify.access")
            logger.info(
                json.dumps({
                    "request_id": rid,
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else "-",
                })
            )
            if response:
                response.headers["X-Request-ID"] = rid


def configure_logging(debug: bool = False) -> None:
    """Set up structured logging for the entire application."""
    level = logging.DEBUG if debug else logging.INFO

    # Format: timestamp | level | request_id | logger | message
    fmt = "%(asctime)s | %(levelname)-7s | %(request_id)s | %(name)s | %(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.setLevel(level)
    # Remove default handlers to avoid duplicate output
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not debug else logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
