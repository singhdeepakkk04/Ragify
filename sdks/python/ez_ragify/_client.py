"""ez-ragify SDK — synchronous and asynchronous HTTP clients."""

from __future__ import annotations

import json
from typing import Any, BinaryIO, Dict, Generator, List, Optional, Union

import httpx

from ez_ragify._exceptions import raise_for_status, RateLimitError
from ez_ragify._types import (
    APIKey,
    APIKeyWithPlaintext,
    Citation,
    Document,
    Model,
    Project,
    ProjectCreate,
    ProjectLogs,
    ProjectUpdate,
    QueryResponse,
    StreamChunk,
    UsageStats,
    UserProfile,
    Feedback,
)

_DEFAULT_BASE_URL = "http://localhost:8000/api/v1"
_DEFAULT_TIMEOUT = 30.0
_STREAM_TIMEOUT = 120.0


# ── helpers ─────────────────────────────────────────────────────────────────

def _build_headers(
    api_key: Optional[str] = None,
    bearer_token: Optional[str] = None,
) -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


# ═══════════════════════════════════════════════════════════════════════════
#  Synchronous Client
# ═══════════════════════════════════════════════════════════════════════════

class EzRagify:
    """Synchronous ez-ragify client.

    Provide **either** ``api_key`` (project-scoped) **or** ``bearer_token``
    (user-scoped). Some endpoints (e.g. project management) require a bearer
    token, while the RAG query endpoint accepts both.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key and not bearer_token:
            raise ValueError("Provide at least one of api_key or bearer_token.")
        self._api_key = api_key
        self._bearer_token = bearer_token
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(api_key, bearer_token),
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "EzRagify":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ── internal ────────────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: Optional[dict] = None,
        files: Optional[dict] = None,
        data: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if json_body is not None:
            kwargs["json"] = json_body
        if params:
            kwargs["params"] = params
        if files:
            kwargs["files"] = files
        if data:
            kwargs["data"] = data
        if timeout:
            kwargs["timeout"] = timeout

        resp = self._client.request(method, path, **kwargs)
        body = resp.json() if resp.content else None
        raise_for_status(resp.status_code, body)
        return body

    # ── RAG Queries ─────────────────────────────────────────────────────────

    def query(
        self,
        query: str,
        project_id: int,
        *,
        top_k: int = 4,
    ) -> QueryResponse:
        """Submit a RAG query and collect the full streamed response."""
        answer_parts: list[str] = []
        citations: list[Citation] = []
        cached = False

        for chunk in self.query_stream(query, project_id, top_k=top_k):
            if chunk.type == "chunk" and chunk.content:
                answer_parts.append(chunk.content)
            elif chunk.type == "citations" and chunk.citations:
                citations = chunk.citations
            elif chunk.type == "done":
                cached = False
            elif chunk.type == "error":
                from ez_ragify._exceptions import EzRagifyError
                raise EzRagifyError(chunk.error or "Unknown streaming error")

        return QueryResponse(
            answer="".join(answer_parts),
            citations=citations,
            cached=cached,
        )

    def query_stream(
        self,
        query: str,
        project_id: int,
        *,
        top_k: int = 4,
    ) -> Generator[StreamChunk, None, None]:
        """Stream a RAG query, yielding ``StreamChunk`` objects."""
        with self._client.stream(
            "POST",
            "/rag/query",
            json={"project_id": project_id, "query": query, "top_k": top_k},
            timeout=_STREAM_TIMEOUT,
        ) as response:
            if response.status_code >= 400:
                body = json.loads(response.read())
                raise_for_status(response.status_code, body)

            for line in response.iter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                chunk_type = data.get("type", "chunk")
                cits = None
                if chunk_type == "citations" and "citations" in data:
                    cits = [Citation(**c) for c in data["citations"]]

                yield StreamChunk(
                    type=chunk_type,
                    content=data.get("content"),
                    citations=cits,
                    error=data.get("error"),
                )

    # ── Projects ────────────────────────────────────────────────────────────

    def create_project(self, project: ProjectCreate) -> Project:
        data = self._request("POST", "/projects", json_body=project.model_dump(exclude_none=True))
        return Project(**data)

    def list_projects(self, *, skip: int = 0, limit: int = 100) -> List[Project]:
        data = self._request("GET", "/projects", params={"skip": skip, "limit": limit})
        return [Project(**p) for p in data]

    def get_project(self, project_id: int) -> Project:
        data = self._request("GET", f"/projects/{project_id}")
        return Project(**data)

    def update_project(self, project_id: int, update: ProjectUpdate) -> Project:
        data = self._request("PATCH", f"/projects/{project_id}", json_body=update.model_dump(exclude_none=True))
        return Project(**data)

    def delete_project(self, project_id: int) -> Project:
        data = self._request("DELETE", f"/projects/{project_id}")
        return Project(**data)

    def list_models(self) -> List[Model]:
        data = self._request("GET", "/projects/models")
        return [Model(**m) for m in data]

    def get_api_key(self, project_id: int) -> APIKey:
        data = self._request("GET", f"/projects/{project_id}/api-key")
        return APIKey(**data)

    def regenerate_api_key(self, project_id: int) -> APIKeyWithPlaintext:
        data = self._request("POST", f"/projects/{project_id}/api-key/regenerate")
        return APIKeyWithPlaintext(**data)

    # ── Documents ───────────────────────────────────────────────────────────

    def upload_document(
        self,
        project_id: int,
        file: Union[BinaryIO, str],
        *,
        filename: Optional[str] = None,
    ) -> Document:
        """Upload a document (PDF, DOCX, TXT, or MD) to a project.

        ``file`` can be a file-like object or a path string.
        """
        if isinstance(file, str):
            import os
            filename = filename or os.path.basename(file)
            fh = open(file, "rb")
            should_close = True
        else:
            fh = file
            filename = filename or getattr(fh, "name", "upload")
            should_close = False

        try:
            data = self._request(
                "POST",
                "/documents/upload",
                files={"file": (filename, fh)},
                data={"project_id": str(project_id)},
                timeout=60.0,
            )
        finally:
            if should_close:
                fh.close()

        return Document(**data)

    def list_documents(self, project_id: int) -> List[Document]:
        data = self._request("GET", "/documents", params={"project_id": project_id})
        return [Document(**d) for d in data]

    def delete_document(self, document_id: int) -> Document:
        data = self._request("DELETE", f"/documents/{document_id}")
        return Document(**data)

    # ── Usage ───────────────────────────────────────────────────────────────

    def get_usage(self) -> UsageStats:
        data = self._request("GET", "/usage/")
        return UsageStats(**data)

    def get_project_logs(
        self,
        project_id: int,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> ProjectLogs:
        data = self._request(
            "GET",
            f"/usage/project/{project_id}",
            params={"limit": limit, "offset": offset},
        )
        return ProjectLogs(**data)

    # ── Feedback ───────────────────────────────────────────────────────────

    def submit_feedback(
        self,
        *,
        project_id: int,
        request_id: str,
        rating: str,
        comment: Optional[str] = None,
    ) -> Feedback:
        body: Dict[str, Any] = {
            "project_id": project_id,
            "request_id": request_id,
            "rating": rating,
        }
        if comment:
            body["comment"] = comment
        data = self._request("POST", "/feedback", json_body=body)
        return Feedback(**data)

    # ── Users ───────────────────────────────────────────────────────────────

    def get_profile(self) -> UserProfile:
        data = self._request("GET", "/users/me")
        return UserProfile(**data)

    def update_profile(self, *, display_name: Optional[str] = None) -> UserProfile:
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        data = self._request("PATCH", "/users/me", json_body=body)
        return UserProfile(**data)

    def delete_account(self) -> dict:
        return self._request("DELETE", "/users/me")


# ═══════════════════════════════════════════════════════════════════════════
#  Async Client
# ═══════════════════════════════════════════════════════════════════════════

class AsyncEzRagify:
    """Asynchronous ez-ragify client (backed by ``httpx.AsyncClient``)."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key and not bearer_token:
            raise ValueError("Provide at least one of api_key or bearer_token.")
        self._api_key = api_key
        self._bearer_token = bearer_token
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(api_key, bearer_token),
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncEzRagify":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # ── internal ────────────────────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: Optional[dict] = None,
        files: Optional[dict] = None,
        data: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        kwargs: Dict[str, Any] = {}
        if json_body is not None:
            kwargs["json"] = json_body
        if params:
            kwargs["params"] = params
        if files:
            kwargs["files"] = files
        if data:
            kwargs["data"] = data
        if timeout:
            kwargs["timeout"] = timeout

        resp = await self._client.request(method, path, **kwargs)
        body = resp.json() if resp.content else None
        raise_for_status(resp.status_code, body)
        return body

    # ── RAG Queries ─────────────────────────────────────────────────────────

    async def query(
        self,
        query: str,
        project_id: int,
        *,
        top_k: int = 4,
    ) -> QueryResponse:
        answer_parts: list[str] = []
        citations: list[Citation] = []
        cached = False

        async for chunk in self.query_stream(query, project_id, top_k=top_k):
            if chunk.type == "chunk" and chunk.content:
                answer_parts.append(chunk.content)
            elif chunk.type == "citations" and chunk.citations:
                citations = chunk.citations
            elif chunk.type == "done":
                cached = False
            elif chunk.type == "error":
                from ez_ragify._exceptions import EzRagifyError
                raise EzRagifyError(chunk.error or "Unknown streaming error")

        return QueryResponse(
            answer="".join(answer_parts),
            citations=citations,
            cached=cached,
        )

    async def query_stream(self, query: str, project_id: int, *, top_k: int = 4):
        """Async generator yielding ``StreamChunk`` objects."""
        async with self._client.stream(
            "POST",
            "/rag/query",
            json={"project_id": project_id, "query": query, "top_k": top_k},
            timeout=_STREAM_TIMEOUT,
        ) as response:
            if response.status_code >= 400:
                body = json.loads(await response.aread())
                raise_for_status(response.status_code, body)

            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                chunk_type = data.get("type", "chunk")
                cits = None
                if chunk_type == "citations" and "citations" in data:
                    cits = [Citation(**c) for c in data["citations"]]

                yield StreamChunk(
                    type=chunk_type,
                    content=data.get("content"),
                    citations=cits,
                    error=data.get("error"),
                )

    # ── Projects ────────────────────────────────────────────────────────────

    async def create_project(self, project: ProjectCreate) -> Project:
        data = await self._request("POST", "/projects", json_body=project.model_dump(exclude_none=True))
        return Project(**data)

    async def list_projects(self, *, skip: int = 0, limit: int = 100) -> List[Project]:
        data = await self._request("GET", "/projects", params={"skip": skip, "limit": limit})
        return [Project(**p) for p in data]

    async def get_project(self, project_id: int) -> Project:
        data = await self._request("GET", f"/projects/{project_id}")
        return Project(**data)

    async def update_project(self, project_id: int, update: ProjectUpdate) -> Project:
        data = await self._request("PATCH", f"/projects/{project_id}", json_body=update.model_dump(exclude_none=True))
        return Project(**data)

    async def delete_project(self, project_id: int) -> Project:
        data = await self._request("DELETE", f"/projects/{project_id}")
        return Project(**data)

    async def list_models(self) -> List[Model]:
        data = await self._request("GET", "/projects/models")
        return [Model(**m) for m in data]

    async def get_api_key(self, project_id: int) -> APIKey:
        data = await self._request("GET", f"/projects/{project_id}/api-key")
        return APIKey(**data)

    async def regenerate_api_key(self, project_id: int) -> APIKeyWithPlaintext:
        data = await self._request("POST", f"/projects/{project_id}/api-key/regenerate")
        return APIKeyWithPlaintext(**data)

    # ── Documents ───────────────────────────────────────────────────────────

    async def upload_document(
        self,
        project_id: int,
        file: Union[BinaryIO, str],
        *,
        filename: Optional[str] = None,
    ) -> Document:
        if isinstance(file, str):
            import os
            filename = filename or os.path.basename(file)
            fh = open(file, "rb")
            should_close = True
        else:
            fh = file
            filename = filename or getattr(fh, "name", "upload")
            should_close = False

        try:
            data = await self._request(
                "POST",
                "/documents/upload",
                files={"file": (filename, fh)},
                data={"project_id": str(project_id)},
                timeout=60.0,
            )
        finally:
            if should_close:
                fh.close()

        return Document(**data)

    async def list_documents(self, project_id: int) -> List[Document]:
        data = await self._request("GET", "/documents", params={"project_id": project_id})
        return [Document(**d) for d in data]

    async def delete_document(self, document_id: int) -> Document:
        data = await self._request("DELETE", f"/documents/{document_id}")
        return Document(**data)

    # ── Usage ───────────────────────────────────────────────────────────────

    async def get_usage(self) -> UsageStats:
        data = await self._request("GET", "/usage/")
        return UsageStats(**data)

    async def get_project_logs(
        self,
        project_id: int,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> ProjectLogs:
        data = await self._request(
            "GET",
            f"/usage/project/{project_id}",
            params={"limit": limit, "offset": offset},
        )
        return ProjectLogs(**data)

    # ── Feedback ───────────────────────────────────────────────────────────

    async def submit_feedback(
        self,
        *,
        project_id: int,
        request_id: str,
        rating: str,
        comment: Optional[str] = None,
    ) -> Feedback:
        body: Dict[str, Any] = {
            "project_id": project_id,
            "request_id": request_id,
            "rating": rating,
        }
        if comment:
            body["comment"] = comment
        data = await self._request("POST", "/feedback", json_body=body)
        return Feedback(**data)

    # ── Users ───────────────────────────────────────────────────────────────

    async def get_profile(self) -> UserProfile:
        data = await self._request("GET", "/users/me")
        return UserProfile(**data)

    async def update_profile(self, *, display_name: Optional[str] = None) -> UserProfile:
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        data = await self._request("PATCH", "/users/me", json_body=body)
        return UserProfile(**data)

    async def delete_account(self) -> dict:
        return await self._request("DELETE", "/users/me")
