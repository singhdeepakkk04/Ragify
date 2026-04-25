"""Tests for user profile endpoint."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_profile(client):
    """GET /users/me should return user profile."""
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@ragify.dev"
    assert data["role"] == "user"


async def test_update_display_name(client):
    """PATCH /users/me should update display_name."""
    resp = await client.patch("/api/v1/users/me", json={"display_name": "Deepak"})
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Deepak"
