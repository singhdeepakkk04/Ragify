"""Tests for RAG query input validation."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_rag_query_empty_string(client):
    """Empty query should be rejected by Pydantic validation."""
    resp = await client.post("/api/v1/rag/query", json={
        "project_id": 1,
        "query": "",
    })
    assert resp.status_code == 422  # Pydantic validation error


async def test_rag_query_too_long(client):
    """Query over 2000 chars should be rejected."""
    resp = await client.post("/api/v1/rag/query", json={
        "project_id": 1,
        "query": "x" * 2001,
    })
    assert resp.status_code == 422


async def test_rag_query_invalid_project_id(client):
    """project_id=0 should be rejected (gt=0)."""
    resp = await client.post("/api/v1/rag/query", json={
        "project_id": 0,
        "query": "test query",
    })
    assert resp.status_code == 422


async def test_rag_query_top_k_out_of_range(client):
    """top_k=100 should be rejected (le=50)."""
    resp = await client.post("/api/v1/rag/query", json={
        "project_id": 1,
        "query": "test query",
        "top_k": 100,
    })
    assert resp.status_code == 422
