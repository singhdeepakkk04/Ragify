import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging_config import configure_logging, StructuredLogMiddleware

# Configure structured logging before anything else
configure_logging(debug=settings.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAGify API",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)


# ── SEC-14: Global request body size limit ───────────────────────────────────
class LimitRequestSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size: int = 25 * 1024 * 1024):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse({"detail": "Request body too large"}, status_code=413)
        return await call_next(request)


# ── SEC-19: HTTP security headers ───────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(LimitRequestSizeMiddleware, max_body_size=25 * 1024 * 1024)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StructuredLogMiddleware)

# ── SEC-04: CORS — externalized origins, restricted methods/headers ──────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Attach request IDs to error responses for traceability."""
    rid = getattr(request.state, "request_id", uuid.uuid4().hex[:12])
    headers = dict(exc.headers or {})
    headers["X-Request-ID"] = rid
    return JSONResponse({"detail": exc.detail, "request_id": rid}, status_code=exc.status_code, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = getattr(request.state, "request_id", uuid.uuid4().hex[:12])
    return JSONResponse({"detail": exc.errors(), "request_id": rid}, status_code=422, headers={"X-Request-ID": rid})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", uuid.uuid4().hex[:12])
    logger.exception("Unhandled server error", exc_info=exc)
    return JSONResponse({"detail": "Internal Server Error", "request_id": rid}, status_code=500, headers={"X-Request-ID": rid})


@app.on_event("startup")
async def verify_auth_config():
    """Ensure at least one JWT verification method is configured."""
    if not settings.SUPABASE_JWT_SECRET and not settings.SUPABASE_URL:
        logger.warning(
            "Neither SUPABASE_JWT_SECRET nor SUPABASE_URL is configured. "
            "JWT authentication will reject all tokens."
        )
    # SEC-04: Warn loudly if production is running with localhost CORS origins
    if not settings.DEBUG:
        localhost_origins = [o for o in settings.cors_origins if "localhost" in o or "127.0.0.1" in o]
        if localhost_origins:
            logger.warning(
                "⚠️  CORS_ALLOWED_ORIGINS contains localhost entries in non-DEBUG mode: %s. "
                "Set CORS_ALLOWED_ORIGINS to your production domain(s) before deploying.",
                localhost_origins,
            )


@app.get("/")
def read_root():
    return {"message": "Welcome to RAGify API"}
