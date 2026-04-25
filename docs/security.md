# RAGify — Comprehensive Security Report

**Date:** 7 March 2026  
**Scope:** Full codebase audit — Backend (FastAPI/Python), Frontend (Next.js/TypeScript), Infrastructure (Docker Compose)  
**Methodology:** OWASP Top 10 (2021), manual code review, static analysis  
**Auditor:** GitHub Copilot Security Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Risk Summary Matrix](#2-risk-summary-matrix)
3. [Critical Findings](#3-critical-findings)
4. [High Findings](#4-high-findings)
5. [Medium Findings](#5-medium-findings)
6. [Low / Informational Findings](#6-low--informational-findings)
7. [OWASP Top 10 Coverage Map](#7-owasp-top-10-coverage-map)
8. [Infrastructure Security](#8-infrastructure-security)
9. [Positive Security Controls](#9-positive-security-controls)
10. [Remediation Roadmap](#10-remediation-roadmap)

---

## 1. Executive Summary

RAGify is a multi-tenant SaaS platform exposing LLM-backed Retrieval-Augmented Generation (RAG) pipelines as REST APIs. The codebase demonstrates a solid security foundation with bcrypt password hashing, parameterized SQL queries, HMAC-hashed API keys, rate limiting, and content guardrails. However, **one critical authentication bypass vulnerability** was identified that must be remediated before any production deployment.

| Severity   | Count |
|------------|-------|
| 🔴 Critical | 1     |
| 🟠 High     | 5     |
| 🟡 Medium   | 8     |
| 🔵 Low      | 6     |
| **Total**  | **20**|

---

## 2. Risk Summary Matrix

| ID     | Title                                              | Severity  | OWASP Category           | File(s)                         |
|--------|----------------------------------------------------|-----------|--------------------------|---------------------------------|
| SEC-01 | JWT Signature Verification Bypass (Fallback Mode) | 🔴 Critical | A07 – Auth Failures      | `backend/app/api/deps.py`       |
| SEC-02 | JWT Claims Not Validated (aud / iss / sub)        | 🟠 High    | A07 – Auth Failures      | `backend/app/api/deps.py`       |
| SEC-03 | JWKS Fetched via urllib (No TLS Pinning)           | 🟠 High    | A02 – Crypto Failures    | `backend/app/api/deps.py`       |
| SEC-04 | CORS Misconfiguration for Production               | 🟠 High    | A05 – Misconfiguration   | `backend/app/main.py`           |
| SEC-05 | No HTTPS Enforced in Frontend or Backend           | 🟠 High    | A02 – Crypto Failures    | `frontend/src/lib/api.ts`       |
| SEC-06 | Hardcoded Default Credentials in Docker Compose   | 🟠 High    | A05 – Misconfiguration   | `docker-compose.yml`            |
| SEC-07 | File Type Validated by Extension Only              | 🟡 Medium  | A03 – Injection          | `backend/app/api/.../documents.py` |
| SEC-08 | Filename Stored Unsanitized from Client            | 🟡 Medium  | A03 – Injection          | `backend/app/api/.../documents.py` |
| SEC-09 | Redis Has No Authentication                        | 🟡 Medium  | A05 – Misconfiguration   | `docker-compose.yml`            |
| SEC-10 | Database Port Exposed on All Interfaces            | 🟡 Medium  | A05 – Misconfiguration   | `docker-compose.yml`            |
| SEC-11 | Database SSL Disabled                              | 🟡 Medium  | A02 – Crypto Failures    | `backend/app/db/session.py`     |
| SEC-12 | Rate Limiting Applied Only to RAG Query            | 🟡 Medium  | A04 – Insecure Design    | `backend/app/core/rate_limiter.py` |
| SEC-13 | Auto-User Creation from Unverified JWT             | 🟡 Medium  | A07 – Auth Failures      | `backend/app/api/deps.py`       |
| SEC-14 | No Global Request Body Size Limit                  | 🟡 Medium  | A04 – Insecure Design    | `backend/app/main.py`           |
| SEC-15 | `get_authenticated_user` Import May Be Undefined  | 🟡 Medium  | A07 – Auth Failures      | `backend/app/core/rate_limiter.py` |
| SEC-16 | SQL `echo=True` Enabled in All Environments        | 🔵 Low     | A09 – Logging Failures   | `backend/app/db/session.py`     |
| SEC-17 | User Query Text Logged in Usage Logs               | 🔵 Low     | A02 – Crypto Failures    | `backend/app/models/usage_log.py` |
| SEC-18 | Sensitive Data Sent to Langfuse Cloud              | 🔵 Low     | A02 – Crypto Failures    | `backend/app/core/tracing.py`   |
| SEC-19 | No HTTP Security Headers                           | 🔵 Low     | A05 – Misconfiguration   | `backend/app/main.py`           |
| SEC-20 | `datetime.utcnow()` Deprecated Usage              | 🔵 Low     | Best Practice            | `backend/app/core/security.py`  |

---

## 3. Critical Findings

---

### SEC-01 — JWT Signature Verification Bypass (Fallback Mode)

**Severity:** 🔴 Critical  
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `backend/app/api/deps.py` (lines 80–87)

#### Description

The `_decode_supabase_jwt` function contains a **last-resort fallback** that, if both HS256 and ES256 verification fail, decodes the JWT token **without verifying its signature at all**. There is no environment guard — this fallback executes in production environments as well as development.

```python
# backend/app/api/deps.py  — VULNERABLE CODE
# 3. Last resort — decode without verification (local dev only)
logger.warning("Falling back to unverified decode")
try:
    return pyjwt.decode(
        token,
        options={"verify_signature": False},   # ← CRITICAL: no sig verification
        algorithms=["HS256", "ES256"],
    )
except Exception as e:
    logger.debug(f"Unverified decode failed: {e}")
    return None
```

#### Attack Scenario

An attacker can craft a JWT with any email payload (e.g., an admin account's email), sign it with a random key, and submit it to the API. If `SUPABASE_JWT_SECRET` is empty and `SUPABASE_URL` is unset (or JWKS is temporarily unreachable), the fallback accepts the forged token. The attacker then gains full access as that user.

Combined with **SEC-13** (auto-user creation), an attacker can also inject entirely new user accounts.

#### Remediation

Remove the fallback entirely. If the token cannot be verified, the request must be rejected.

```python
# FIXED: Remove the unverified fallback block entirely
# After trying HS256 and ES256 without success, return None
logger.warning("JWT verification failed: no valid verification method available")
return None
```

Additionally, add a startup assertion to ensure at least one verification method is configured:

```python
# In app/main.py or startup event
@app.on_event("startup")
async def verify_auth_config():
    if not settings.SUPABASE_JWT_SECRET and not settings.SUPABASE_URL:
        raise RuntimeError(
            "FATAL: Neither SUPABASE_JWT_SECRET nor SUPABASE_URL configured. "
            "Authentication cannot be performed securely."
        )
```

---

## 4. High Findings

---

### SEC-02 — JWT Claims Not Validated (aud / iss / sub)

**Severity:** 🟠 High  
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `backend/app/api/deps.py` (lines 26–35)

#### Description

JWT signature validation is performed, but the `aud` (audience), `iss` (issuer), and `sub` (subject) claims are explicitly disabled:

```python
options = {
    "verify_aud": False,   # ← Not verified
    "verify_iss": False,   # ← Not verified
    "verify_sub": False,   # ← Not verified
    "verify_exp": True,
}
```

A valid JWT issued by a **different** Supabase project (or completely different identity provider) sharing the same algorithm would be accepted as long as it passes signature verification.

#### Remediation

Validate `iss` against your own Supabase project URL:

```python
options = {
    "verify_aud": False,        # Supabase sets aud="authenticated" — safe to verify
    "verify_iss": True,
    "verify_sub": True,
    "verify_exp": True,
}
# And pass issuer to decode():
return pyjwt.decode(
    token, secret, algorithms=["HS256"],
    options=options,
    issuer=f"{settings.SUPABASE_URL}/auth/v1"
)
```

---

### SEC-03 — JWKS Endpoint Fetched via urllib (No TLS Certificate Pinning)

**Severity:** 🟠 High  
**OWASP:** A02 – Cryptographic Failures  
**File:** `backend/app/api/deps.py` (lines 56–70)

#### Description

The JWKS endpoint is fetched using `urllib.request.urlopen` with only a 5-second timeout. There is no:
- TLS certificate validation
- Certificate pinning
- Request caching (a fresh HTTP call is made on **every** request for ES256 tokens)

```python
with urllib.request.urlopen(jwks_url, timeout=5) as resp:
    jwks = _json.loads(resp.read())
```

This is also a **Denial of Service vector**: every authenticated request makes a network roundtrip to Supabase. If Supabase is slow, your API is slow. If the JWKS endpoint returns garbage, the token falls through to the unverified fallback (SEC-01).

#### Remediation

1. Use the `requests` or `httpx` library (already in the dependency tree via FastAPI) for TLS-verified calls.
2. Cache the JWKS response with a TTL (e.g., 24 hours) and refresh only on key rotation.

```python
import httpx
from cachetools import TTLCache
import threading

_jwks_cache = TTLCache(maxsize=1, ttl=86400)  # 24-hour cache
_jwks_lock = threading.Lock()

def _get_jwks(supabase_url: str) -> dict:
    with _jwks_lock:
        if "jwks" in _jwks_cache:
            return _jwks_cache["jwks"]
        resp = httpx.get(
            f"{supabase_url.rstrip('/')}/.well-known/jwks.json",
            timeout=5.0,
            verify=True,   # Enforce TLS verification
        )
        resp.raise_for_status()
        _jwks_cache["jwks"] = resp.json()
        return _jwks_cache["jwks"]
```

---

### SEC-04 — CORS Misconfiguration for Production

**Severity:** 🟠 High  
**OWASP:** A05 – Security Misconfiguration  
**File:** `backend/app/main.py`

#### Description

The CORS origin is hardcoded to `http://localhost:3000` and uses wildcard methods and headers:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Hardcoded dev URL
    allow_credentials=True,
    allow_methods=["*"],                       # All methods
    allow_headers=["*"],                       # All headers
)
```

In production, `http://localhost:3000` will reject all legitimate browser requests. `allow_methods=["*"]` with `allow_credentials=True` is also problematic as it allows credentialed cross-origin requests from the one allowed origin for any HTTP verb.

#### Remediation

Externalize the allowed origin and restrict methods:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,  # From environment
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)
```

Add to config:
```python
class Settings(BaseSettings):
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
```

---

### SEC-05 — No HTTPS Enforced in Frontend or Backend

**Severity:** 🟠 High  
**OWASP:** A02 – Cryptographic Failures  
**File:** `frontend/src/lib/api.ts`

#### Description

The API base URL is hardcoded as plaintext HTTP:

```typescript
// frontend/src/lib/api.ts
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',  // ← HTTP, no TLS
```

Bearer tokens (JWT, API keys) are transmitted over an unencrypted connection. Any network observer (ISP, Wi-Fi operator, etc.) on a non-localhost deployment can read and replay these tokens.

#### Remediation

Make the API URL configurable via an environment variable and enforce HTTPS in production:

```typescript
const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});
```

Add a Next.js environment check:
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourproductiondomain.com/api/v1
```

The backend should also run behind a TLS-terminating reverse proxy (Nginx/Caddy/Traefik) in production.

---

### SEC-06 — Hardcoded Default Credentials in Docker Compose

**Severity:** 🟠 High  
**OWASP:** A05 – Security Misconfiguration  
**File:** `docker-compose.yml`

#### Description

The PostgreSQL database password is hardcoded directly in source control:

```yaml
environment:
    POSTGRES_USER: ragify
    POSTGRES_PASSWORD: ragify_password   # ← Hardcoded, weak
    POSTGRES_DB: ragify_db
```

Additionally, Redis has no authentication (`requirepass` not configured), so any process with network access to port 6379 can read/write cache data — including the query cache, which contains user query responses.

#### Remediation

Use Docker secrets or an external `.env` file not committed to git:

```yaml
environment:
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
```

For Redis, add a password:
```yaml
redis:
    command: redis-server --requirepass "${REDIS_PASSWORD}"
```

And update the rate limiter to include the password in the Redis URL.

---

## 5. Medium Findings

---

### SEC-07 — File Type Validated by Extension Only

**Severity:** 🟡 Medium  
**OWASP:** A03 – Injection  
**File:** `backend/app/api/api_v1/endpoints/documents.py`

#### Description

File type is determined by checking the filename extension from the client:

```python
if file.filename.endswith(".pdf"):
    ...
elif file.filename.endswith(".docx"):
    ...
```

An attacker can rename a malicious file (e.g., a ZIP bomb, a crafted DOCX with macros, or a file designed to crash `pypdf`) and upload it as a `.pdf`.

#### Remediation

Validate the MIME type via magic bytes detection using the `python-magic` library:

```python
import magic

def validate_file_type(file_bytes: bytes, expected_extension: str) -> bool:
    mime = magic.from_buffer(file_bytes[:2048], mime=True)
    allowed_mimes = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".md": "text/plain",
    }
    return mime == allowed_mimes.get(expected_extension)
```

---

### SEC-08 — Filename Stored Unsanitized from Client

**Severity:** 🟡 Medium  
**OWASP:** A03 – Injection  
**File:** `backend/app/api/api_v1/endpoints/documents.py`

#### Description

The filename submitted by the client is stored directly in the database without sanitization:

```python
doc_in = doc_schemas.DocumentCreate(
    filename=file.filename,   # ← Raw client-supplied value
    project_id=project_id,
)
```

If the filename is later rendered in the UI without proper escaping (e.g., in a React component that uses `dangerouslySetInnerHTML`), this can lead to stored XSS. Path traversal attacks are also a risk if the filename is ever used to construct a filesystem path.

#### Remediation

```python
import os

safe_filename = os.path.basename(file.filename or "unknown_file")
# Optionally strip non-printable/special characters
safe_filename = "".join(c for c in safe_filename if c.isprintable() and c not in '<>"\'\\/')
doc_in = doc_schemas.DocumentCreate(filename=safe_filename[:255], project_id=project_id)
```

---

### SEC-09 — Redis Has No Authentication

**Severity:** 🟡 Medium  
**OWASP:** A05 – Security Misconfiguration  
**File:** `docker-compose.yml`

#### Description

The Redis container is started without a password and listens on all interfaces by default. Any process that can reach port 6379 (including other Docker containers on the same network, or external hosts if the Docker host has open ports) can:

- Read and modify rate limiting counters (bypassing rate limits)
- Read, write, or delete cached RAG responses
- Enumerate all cache keys

#### Remediation

See SEC-06 remediation. Additionally, configure the Redis bind to only the Docker internal network:

```yaml
redis:
    command: redis-server --requirepass "${REDIS_PASSWORD}" --bind 127.0.0.1
```

---

### SEC-10 — Database and Redis Ports Exposed on All Interfaces

**Severity:** 🟡 Medium  
**OWASP:** A05 – Security Misconfiguration  
**File:** `docker-compose.yml`

#### Description

Both services expose their ports with `ports:` binding to `0.0.0.0` by default:

```yaml
db:
    ports:
        - "5432:5432"   # Accessible from any network interface
redis:
    ports:
        - "6379:6379"   # Accessible from any network interface
```

In a cloud environment (AWS EC2, GCP VM, etc.) where the instance has a public IP, these ports would be reachable from the internet unless a firewall explicitly blocks them.

#### Remediation

Bind to localhost only — the backend container communicates via the Docker internal network:

```yaml
db:
    ports:
        - "127.0.0.1:5432:5432"
redis:
    ports:
        - "127.0.0.1:6379:6379"
```

Or remove the `ports:` declaration entirely and use Docker service names for internal connectivity.

---

### SEC-11 — Database Connection Has SSL Disabled

**Severity:** 🟡 Medium  
**OWASP:** A02 – Cryptographic Failures  
**File:** `backend/app/db/session.py`

#### Description

The database engine is explicitly created without SSL connection arguments. The code comment acknowledges this and identifies it as a migration risk:

```python
# NOTE: No SSL connect_args here — local Docker postgres doesn't use SSL.
# If switching back to Supabase, add: connect_args={"ssl": "require"}
engine = create_async_engine(settings.DATABASE_URL, echo=True)
```

If the application is deployed with a remote PostgreSQL instance (Supabase, RDS, etc.) and the developer forgets to add `ssl: "require"`, all database traffic (including embedded vectors, user queries, and user email addresses) is transmitted in plaintext.

#### Remediation

Make SSL configurable and default to required:

```python
import ssl

def build_engine():
    ssl_mode = getattr(settings, "DB_SSL_MODE", "require")
    connect_args = {}
    if ssl_mode != "disable":
        ssl_ctx = ssl.create_default_context()
        connect_args["ssl"] = ssl_ctx
    return create_async_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DEBUG,
    )

engine = build_engine()
```

---

### SEC-12 — Rate Limiting Applied Only to RAG Query Endpoint

**Severity:** 🟡 Medium  
**OWASP:** A04 – Insecure Design  
**File:** `backend/app/core/rate_limiter.py`

#### Description

The rate limiter (`check_rate_limit` dependency) is only applied to the `POST /rag/query` endpoint. The following endpoints have no rate limiting:

- `POST /documents/upload` — an attacker can upload thousands of large files
- `POST /projects` — unlimited project creation
- `POST /projects/{id}/api-key/regenerate` — unlimited key rotation

This enables abuse scenarios:
1. DoS the indexing worker pool by flooding with document uploads
2. Exhaust storage by creating unlimited projects with documents
3. Invalidate legitimate API keys by repeatedly triggering regeneration

#### Remediation

Apply rate limiting globally via middleware, or extend the `check_rate_limit` dependency to all mutation endpoints. A global approach using a middleware is preferred:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Per-endpoint limits
@router.post("/upload")
@limiter.limit("20/minute")
async def upload_document(...):
    ...
```

---

### SEC-13 — Auto-User Creation from Unverified JWT

**Severity:** 🟡 Medium  
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `backend/app/api/deps.py` (lines 100–117)

#### Description

When a JWT is decoded and the email does not exist in the local database, a new user account is **automatically created**:

```python
if user is None:
    user = User(
        email=email,
        hashed_password=_secrets.token_hex(32),
        is_active=True,
        role="user",
    )
    db.add(user)
    await db.commit()
```

Combined with **SEC-01** (unverified JWT fallback), an attacker could auto-provision accounts for arbitrary email addresses by submitting forged JWTs. Even without SEC-01, this pattern means that any valid Supabase user (regardless of whether they're supposed to have backend access) automatically becomes provisioned.

#### Remediation

Consider requiring explicit registration/invitation instead of auto-provisioning. At minimum, ensure this code only runs when a verified, non-fallback JWT was used:

```python
if user is None and token_was_verified:  # Add a flag from _decode_supabase_jwt
    user = User(...)
elif user is None:
    return None  # Do not create user from unverified token
```

---

### SEC-14 — No Global Request Body Size Limit

**Severity:** 🟡 Medium  
**OWASP:** A04 – Insecure Design  
**File:** `backend/app/main.py`

#### Description

FastAPI / Starlette has no default request body size limit. While document uploads check file size (20 MB), JSON endpoints like `POST /rag/query` or `POST /projects` have no limit. An attacker can send a multi-megabyte JSON body to these endpoints to:

- Consume server memory
- Slow down the JSON parsing process
- Cause OOM on constrained servers

#### Remediation

Add a body size limit middleware:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class LimitRequestSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size: int = 1 * 1024 * 1024):  # 1 MB default
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-length"):
            if int(request.headers["content-length"]) > self.max_body_size:
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail": "Request body too large"}, status_code=413)
        return await call_next(request)

app.add_middleware(LimitRequestSizeMiddleware, max_body_size=25 * 1024 * 1024)  # 25 MB global cap
```

---

### SEC-15 — `get_authenticated_user` Import May Be Undefined

**Severity:** 🟡 Medium  
**OWASP:** A07 – Identification and Authentication Failures  
**File:** `backend/app/core/rate_limiter.py`

#### Description

The rate limiter imports `get_authenticated_user` from `app.api.deps`:

```python
from app.api.deps import get_authenticated_user
```

However, `deps.py` only defines `get_current_user`, `get_current_active_user`, `get_current_active_admin`, and related helpers. No `get_authenticated_user` function is visible in the file. This either:

1. **Causes an `ImportError` at startup** — the entire application fails to load
2. **Indicates a function with dual-auth (API Key + JWT) is missing** — the rate limiter may be silently bypassed

This must be investigated and verified. If the dual-auth dependency is missing, API key authenticated users may bypass rate limiting entirely.

#### Remediation

Verify that `get_authenticated_user` exists in `deps.py`. If not, create it:

```python
async def get_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> User:
    """Resolve user from either API Key or JWT Bearer token."""
    # Try API Key first
    if x_api_key:
        user = await get_user_from_api_key(db, x_api_key, request)
        if user:
            return user
    # Fall back to JWT
    if credentials:
        user = await get_user_from_token(db, credentials.credentials)
        if user:
            return user
    raise HTTPException(status_code=401, detail="Not authenticated")
```

---

## 6. Low / Informational Findings

---

### SEC-16 — SQL `echo=True` Enabled in All Environments

**Severity:** 🔵 Low  
**OWASP:** A09 – Security Logging and Monitoring Failures  
**File:** `backend/app/db/session.py`

**Issue:** `create_async_engine(..., echo=True)` logs all SQL statements — including embedded vector arrays and user query text — to stdout/stderr in every environment.

**Fix:** Tie `echo` to a debug flag:
```python
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
```

---

### SEC-17 — User Query Text Logged in Usage Logs

**Severity:** 🔵 Low  
**OWASP:** A02 – Cryptographic Failures (data-at-rest privacy)  
**File:** `backend/app/models/usage_log.py`, `backend/app/api/api_v1/endpoints/usage.py`

**Issue:** The full plaintext query (e.g., "What are the tax exemptions for my ITR?") is stored in `usage_logs` and returned in the recent queries API response. Users querying sensitive documents expect query confidentiality.

**Fix:** Store a hash or truncated version for analytics purposes. If full queries are needed for debugging, encrypt them at rest and restrict access to admin roles only.

---

### SEC-18 — Sensitive Data Sent to Langfuse Cloud

**Severity:** 🔵 Low  
**OWASP:** A02 – Cryptographic Failures  
**File:** `backend/app/core/tracing.py`, `backend/app/core/rag/retrieval.py`

**Issue:** When `LANGFUSE_SECRET_KEY` is configured, LangFuse traces include `user_id`, project metadata, and the full query text, which are sent to `cloud.langfuse.com`. This is a third-party SAAS service.

**Fix:** Review data residency requirements. If PII or sensitive document content may be in queries, use Langfuse's self-hosted option or anonymize `user_id` in traces.

---

### SEC-19 — No HTTP Security Headers

**Severity:** 🔵 Low  
**OWASP:** A05 – Security Misconfiguration  
**File:** `backend/app/main.py`

**Issue:** The API does not set security headers. While primarily a browser-facing concern, missing headers like `X-Content-Type-Options`, `X-Frame-Options`, and `Strict-Transport-Security` reduce defense-in-depth.

**Fix:**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
```

---

### SEC-20 — `datetime.utcnow()` Deprecated Usage

**Severity:** 🔵 Low  
**OWASP:** Best Practice  
**File:** `backend/app/core/security.py`

**Issue:** `datetime.utcnow()` is deprecated since Python 3.12 and returns a timezone-naive datetime, which can cause subtle expiry calculation bugs.

**Fix:**
```python
from datetime import datetime, timezone
expire = datetime.now(timezone.utc) + expires_delta
```

---

## 7. OWASP Top 10 Coverage Map

| OWASP Category                                | Status    | Finding IDs        |
|-----------------------------------------------|-----------|--------------------|
| A01 – Broken Access Control                   | ✅ Covered | (project ownership checks in all endpoints) |
| A02 – Cryptographic Failures                  | ⚠️ Issues  | SEC-03, SEC-05, SEC-11, SEC-17, SEC-18 |
| A03 – Injection                               | ⚠️ Issues  | SEC-07, SEC-08 (SQL injection mitigated via parameterized queries) |
| A04 – Insecure Design                         | ⚠️ Issues  | SEC-12, SEC-14       |
| A05 – Security Misconfiguration               | ⚠️ Issues  | SEC-04, SEC-06, SEC-09, SEC-10, SEC-19 |
| A06 – Vulnerable and Outdated Components      | ✅ Low Risk | (regular dependency audit recommended) |
| A07 – Identification and Authentication Failures | 🔴 Critical | SEC-01, SEC-02, SEC-13, SEC-15 |
| A08 – Software and Data Integrity Failures    | ✅ Covered  | (API keys hashed; no deserialization of untrusted data) |
| A09 – Security Logging and Monitoring Failures | ⚠️ Issues  | SEC-16              |
| A10 – Server-Side Request Forgery (SSRF)      | ⚠️ Medium  | SEC-03 (JWKS urllib) — could be SSRF if URL is user-controlled in future |

---

## 8. Infrastructure Security

### Docker Compose Analysis

| Component   | Issue                                     | Risk   |
|-------------|-------------------------------------------|--------|
| PostgreSQL  | `POSTGRES_PASSWORD: ragify_password` hardcoded | High |
| PostgreSQL  | Port 5432 exposed on `0.0.0.0`           | Medium |
| Redis       | No `requirepass` configured              | Medium |
| Redis       | Port 6379 exposed on `0.0.0.0`           | Medium |
| Backend     | Not included in docker-compose (runs separately) | Info |
| TLS         | No reverse proxy / TLS termination configured | High |

### Network Segmentation

The current `docker-compose.yml` does not define explicit Docker networks. All containers share the default bridge network, meaning any container can reach any other container. Recommendation: define explicit named networks and use `internal: true` for database networks.

```yaml
networks:
    backend_net:
        internal: false   # backend can reach internet (for OpenAI API)
    db_net:
        internal: true    # DB is only accessible internally

services:
    db:
        networks: [db_net]
    redis:
        networks: [db_net]
    backend:
        networks: [backend_net, db_net]
```

---

## 9. Positive Security Controls

The following security controls are correctly implemented and should be preserved:

| Control | Implementation | Location |
|---------|---------------|----------|
| Password Hashing | bcrypt via `passlib` | `backend/app/core/security.py` |
| SQL Injection Prevention | Parameterized queries (`text()` with named params) throughout | `backend/app/core/rag/retrieval.py` |
| API Key Storage | SHA-256 hash stored, plaintext shown once | `backend/app/crud/apikey.py` |
| API Key Scoping | Keys validated against project ownership | `backend/app/api/api_v1/endpoints/rag.py` |
| Multi-tenant Isolation | `user_id` denormalized on chunks; WHERE on every query | `backend/app/core/rag/retrieval.py` |
| Rate Limiting | Redis sliding-window per user | `backend/app/core/rate_limiter.py` |
| Content Guardrails | Keyword blocklist + injection pattern matching | `backend/app/core/guardrails.py` |
| Query Cache Isolation | Cache key includes `user_id + project_id` | `backend/app/core/query_cache.py` |
| Project Ownership Check | All document/project operations check `owner_id` | All endpoint files |
| File Size Limit | 20 MB hard limit on uploads | `backend/app/api/api_v1/endpoints/documents.py` |
| Input Sanitization (Query) | `check_input()` strips and validates before RAG | `backend/app/core/guardrails.py` |
| Supabase RLS | Row-level security policies in SQL | `supabase/rls_policies.sql` |
| Secure Token Generation | `secrets.token_urlsafe(32)` for API keys | `backend/app/crud/apikey.py` |
| JWT Expiry Enforced | `verify_exp: True` in all JWT decode calls | `backend/app/api/deps.py` |

---

## 10. Remediation Roadmap

### Immediate (Before Production Deploy)

| Priority | ID     | Action                                      | Effort |
|----------|--------|---------------------------------------------|--------|
| P0       | SEC-01 | Remove JWT unverified fallback              | 30 min |
| P0       | SEC-02 | Add issuer/subject claim validation         | 1 hr   |
| P0       | SEC-06 | Move credentials to `.env` (out of git)     | 1 hr   |

### Short Term (Sprint 1)

| Priority | ID     | Action                                      | Effort |
|----------|--------|---------------------------------------------|--------|
| P1       | SEC-03 | Cache JWKS with TTL; use httpx with TLS     | 2 hrs  |
| P1       | SEC-04 | Externalize CORS origins via env config     | 1 hr   |
| P1       | SEC-05 | Externalize API base URL; enforce HTTPS     | 1 hr   |
| P1       | SEC-09 | Add Redis password; restrict bind IP        | 1 hr   |
| P1       | SEC-10 | Restrict DB/Redis port bindings             | 30 min |
| P1       | SEC-15 | Verify/create `get_authenticated_user`      | 1 hr   |

### Medium Term (Sprint 2)

| Priority | ID     | Action                                       | Effort |
|----------|--------|----------------------------------------------|--------|
| P2       | SEC-07 | Add magic-byte MIME validation for uploads   | 3 hrs  |
| P2       | SEC-08 | Sanitize uploaded filenames                  | 1 hr   |
| P2       | SEC-11 | Make DB SSL configurable; default to require | 1 hr   |
| P2       | SEC-12 | Extend rate limiting to upload/project endpoints | 2 hrs |
| P2       | SEC-13 | Add guard on auto-user creation              | 1 hr   |
| P2       | SEC-14 | Add global request body size middleware      | 1 hr   |

### Ongoing

| Priority | ID     | Action                                      |
|----------|--------|---------------------------------------------|
| P3       | SEC-16 | Set `echo=settings.DEBUG` in DB engine      |
| P3       | SEC-17 | Audit query storage for PII                 |
| P3       | SEC-18 | Review Langfuse data residency              |
| P3       | SEC-19 | Add HTTP security headers middleware        |
| P3       | SEC-20 | Replace `datetime.utcnow()` with timezone-aware |

---

*Report generated by GitHub Copilot Security Review — 7 March 2026*
