"""Unit tests for the ez-ragify Python SDK."""

import json
import pytest
import httpx
import respx

from ez_ragify import EzRagify, AsyncEzRagify
from ez_ragify._exceptions import (
    AuthenticationError,
    NotFoundError,
    EzRagifyError,
    RateLimitError,
    ValidationError,
)
from ez_ragify._types import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    Document,
    QueryResponse,
    UsageStats,
    ProjectLogs,
    UserProfile,
    APIKey,
    APIKeyWithPlaintext,
    Model,
)

BASE = "http://test.local/api/v1"


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    c = EzRagify(api_key="rag_test123", base_url=BASE)
    yield c
    c.close()


# ── Initialization ──────────────────────────────────────────────────────────

def test_requires_auth():
    with pytest.raises(ValueError, match="api_key or bearer_token"):
        EzRagify()


def test_api_key_header():
    c = EzRagify(api_key="rag_abc", base_url=BASE)
    assert c._client.headers["X-API-Key"] == "rag_abc"
    c.close()


def test_bearer_header():
    c = EzRagify(bearer_token="tok_xyz", base_url=BASE)
    assert c._client.headers["Authorization"] == "Bearer tok_xyz"
    c.close()


def test_context_manager():
    with EzRagify(api_key="rag_test", base_url=BASE) as c:
        assert c._client is not None


# ── Error Handling ──────────────────────────────────────────────────────────

@respx.mock
def test_401_raises_auth_error(client):
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(401, json={"detail": "Not authenticated"})
    )
    with pytest.raises(AuthenticationError):
        client.get_profile()


@respx.mock
def test_404_raises_not_found(client):
    respx.get(f"{BASE}/projects/999").mock(
        return_value=httpx.Response(404, json={"detail": "Project not found"})
    )
    with pytest.raises(NotFoundError):
        client.get_project(999)


@respx.mock
def test_422_raises_validation_error(client):
    respx.post(f"{BASE}/projects").mock(
        return_value=httpx.Response(422, json={"detail": "Validation error"})
    )
    with pytest.raises(ValidationError):
        client.create_project(ProjectCreate(name="x", project_type="BYOR"))


@respx.mock
def test_429_raises_rate_limit(client):
    respx.get(f"{BASE}/usage/").mock(
        return_value=httpx.Response(429, json={"detail": "Too many requests"})
    )
    with pytest.raises(RateLimitError):
        client.get_usage()


@respx.mock
def test_500_raises_server_error(client):
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(500, json={"detail": "Internal server error"})
    )
    with pytest.raises(EzRagifyError):
        client.get_profile()


# ── Projects ────────────────────────────────────────────────────────────────

_PROJECT_JSON = {
    "id": 1,
    "owner_id": 10,
    "name": "Tax Bot",
    "description": "Tax helper",
    "project_type": "ITR",
    "llm_model": "gpt-3.5-turbo",
    "embedding_model": "text-embedding-3-small",
    "temperature": 0.0,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "top_k": 4,
    "deployment_environment": "dev",
    "is_public": False,
    "config": None,
    "created_at": "2025-01-01T00:00:00",
}


@respx.mock
def test_create_project(client):
    respx.post(f"{BASE}/projects").mock(
        return_value=httpx.Response(200, json=_PROJECT_JSON)
    )
    project = client.create_project(ProjectCreate(name="Tax Bot", project_type="ITR"))
    assert isinstance(project, Project)
    assert project.id == 1
    assert project.name == "Tax Bot"


@respx.mock
def test_list_projects(client):
    respx.get(f"{BASE}/projects").mock(
        return_value=httpx.Response(200, json=[_PROJECT_JSON])
    )
    projects = client.list_projects()
    assert len(projects) == 1
    assert projects[0].project_type == "ITR"


@respx.mock
def test_get_project(client):
    respx.get(f"{BASE}/projects/1").mock(
        return_value=httpx.Response(200, json=_PROJECT_JSON)
    )
    p = client.get_project(1)
    assert p.name == "Tax Bot"


@respx.mock
def test_update_project(client):
    updated = {**_PROJECT_JSON, "name": "Updated Bot"}
    respx.patch(f"{BASE}/projects/1").mock(
        return_value=httpx.Response(200, json=updated)
    )
    p = client.update_project(1, ProjectUpdate(name="Updated Bot"))
    assert p.name == "Updated Bot"


@respx.mock
def test_delete_project(client):
    respx.delete(f"{BASE}/projects/1").mock(
        return_value=httpx.Response(200, json=_PROJECT_JSON)
    )
    p = client.delete_project(1)
    assert p.id == 1


# ── Models ──────────────────────────────────────────────────────────────────

@respx.mock
def test_list_models(client):
    respx.get(f"{BASE}/projects/models").mock(
        return_value=httpx.Response(200, json=[
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"},
        ])
    )
    models = client.list_models()
    assert len(models) == 1
    assert models[0].id == "gpt-4o"


# ── API Keys ────────────────────────────────────────────────────────────────

@respx.mock
def test_get_api_key(client):
    respx.get(f"{BASE}/projects/1/api-key").mock(
        return_value=httpx.Response(200, json={
            "id": 1,
            "name": "Default Key",
            "project_id": 1,
            "prefix": "rag_abc...",
            "is_active": True,
            "created_at": "2025-01-01T00:00:00",
        })
    )
    key = client.get_api_key(1)
    assert isinstance(key, APIKey)


@respx.mock
def test_regenerate_api_key(client):
    respx.post(f"{BASE}/projects/1/api-key/regenerate").mock(
        return_value=httpx.Response(200, json={
            "id": 2,
            "name": "Default Key",
            "project_id": 1,
            "prefix": "rag_xyz...",
            "is_active": True,
            "created_at": "2025-01-01T00:00:00",
            "plaintext_key": "rag_xyz_full_key_here",
        })
    )
    key = client.regenerate_api_key(1)
    assert isinstance(key, APIKeyWithPlaintext)
    assert key.plaintext_key == "rag_xyz_full_key_here"


# ── Documents ───────────────────────────────────────────────────────────────

_DOC_JSON = {
    "id": 5,
    "filename": "report.pdf",
    "project_id": 1,
    "status": "indexed",
    "created_at": "2025-01-01T00:00:00",
}


@respx.mock
def test_upload_document_from_path(client):
    respx.post(f"{BASE}/documents/upload").mock(
        return_value=httpx.Response(200, json=_DOC_JSON)
    )
    # use BinaryIO path flow
    p = client.upload_document(1, __file__)
    assert isinstance(p, Document)


@respx.mock
def test_list_documents(client):
    respx.get(f"{BASE}/documents").mock(
        return_value=httpx.Response(200, json=[_DOC_JSON])
    )
    docs = client.list_documents(1)
    assert len(docs) == 1


@respx.mock
def test_delete_document(client):
    respx.delete(f"{BASE}/documents/5").mock(
        return_value=httpx.Response(200, json=_DOC_JSON)
    )
    doc = client.delete_document(5)
    assert doc.id == 5


# ── Usage ───────────────────────────────────────────────────────────────

_USAGE_JSON = {
    "total_queries": 100,
    "total_documents": 5,
    "total_projects": 3,
    "queries_today": 10,
    "queries_this_week": 50,
    "avg_latency_ms": 123,
    "rate_limit": {
        "limit": 10,
        "remaining": 7,
        "used": 3,
        "window_seconds": 60,
    },
    "model_breakdown": [
        {"model": "gpt-3.5-turbo", "count": 80},
        {"model": "gpt-4o", "count": 20},
    ],
    "project_breakdown": [
        {"project": "Policy 2024", "queries": 95, "avg_latency": 1100.2}
    ],
    "recent_queries": [
        {
            "query": "What is...",
            "model": "gpt-3.5-turbo",
            "latency_ms": 1234,
            "timestamp": "2024-01-15T10:30:00Z",
            "project": "Policy 2024",
        }
    ],
    "daily_usage": [
        {"date": "2024-01-09", "queries": 5},
        {"date": "2024-01-10", "queries": 8},
    ],
}


@respx.mock
def test_get_usage(client):
    respx.get(f"{BASE}/usage/").mock(
        return_value=httpx.Response(200, json=_USAGE_JSON)
    )
    usage = client.get_usage()
    assert usage.total_queries == 100


@respx.mock
def test_get_project_logs(client):
    respx.get(f"{BASE}/usage/project/1").mock(
        return_value=httpx.Response(200, json={"total": 1, "logs": []})
    )
    logs = client.get_project_logs(1)
    assert isinstance(logs, ProjectLogs)


# ── Users ────────────────────────────────────────────────────────────────

_PROFILE_JSON = {
    "id": 1,
    "email": "test@example.com",
    "display_name": "User",
    "role": "user",
    "is_active": True,
}


@respx.mock
def test_get_profile(client):
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(200, json=_PROFILE_JSON)
    )
    profile = client.get_profile()
    assert profile.email == "test@example.com"


@respx.mock
def test_update_profile(client):
    respx.patch(f"{BASE}/users/me").mock(
        return_value=httpx.Response(200, json={**_PROFILE_JSON, "display_name": "Updated"})
    )
    profile = client.update_profile(display_name="Updated")
    assert profile.display_name == "Updated"


@respx.mock
def test_delete_account(client):
    respx.delete(f"{BASE}/users/me").mock(
        return_value=httpx.Response(200, json={"detail": "Account deleted"})
    )
    result = client.delete_account()
    assert result["detail"] == "Account deleted"


# ── RAG Query (streaming mock) ─────────────────────────────────────────────

@respx.mock
def test_query_collects_stream(client):
    ndjson = (
        json.dumps({"type": "chunk", "content": "Hello "}) + "\n"
        + json.dumps({"type": "chunk", "content": "world"}) + "\n"
        + json.dumps({"type": "citations", "citations": [
            {"filename": "doc.pdf", "page_number": 1, "snippet": "Hello world"}
        ]}) + "\n"
        + json.dumps({"type": "done"}) + "\n"
    )
    respx.post(f"{BASE}/rag/query").mock(
        return_value=httpx.Response(
            200,
            content=ndjson.encode(),
            headers={"content-type": "application/x-ndjson"},
        )
    )
    response = client.query("greet me", project_id=1)
    assert isinstance(response, QueryResponse)
    assert response.answer == "Hello world"
    assert len(response.citations) == 1
    assert response.citations[0].filename == "doc.pdf"


# ── Async Client ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@respx.mock
async def test_async_list_projects():
    respx.get(f"{BASE}/projects").mock(
        return_value=httpx.Response(200, json=[_PROJECT_JSON])
    )
    async with AsyncEzRagify(api_key="rag_test", base_url=BASE) as client:
        projects = await client.list_projects()
        assert len(projects) == 1


@pytest.mark.asyncio
@respx.mock
async def test_async_get_usage():
    respx.get(f"{BASE}/usage/").mock(
        return_value=httpx.Response(200, json=_USAGE_JSON)
    )
    async with AsyncEzRagify(api_key="rag_test", base_url=BASE) as client:
        usage = await client.get_usage()
        assert usage.total_queries == 100


@pytest.mark.asyncio
@respx.mock
async def test_async_get_profile():
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(200, json=_PROFILE_JSON)
    )
    async with AsyncEzRagify(bearer_token="tok", base_url=BASE) as client:
        profile = await client.get_profile()
        assert profile.email == "test@example.com"
