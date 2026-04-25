"""Tests for project CRUD endpoints."""

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


async def test_create_project(client):
    """POST /projects should create a project."""
    resp = await client.post("/api/v1/projects", json={
        "name": "Test Project",
        "description": "A test project",
        "project_type": "byor",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Project"
    assert data["project_type"] == "byor"
    assert "id" in data


async def test_list_projects(client):
    """GET /projects should return user's projects."""
    # Create first
    await client.post("/api/v1/projects", json={
        "name": "P1", "project_type": "byor",
    })
    resp = await client.get("/api/v1/projects")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_project_not_found(client):
    """GET /projects/999 should 404."""
    resp = await client.get("/api/v1/projects/999")
    assert resp.status_code == 404


async def test_delete_project_not_found(client):
    """DELETE /projects/999 should 404."""
    resp = await client.delete("/api/v1/projects/999")
    assert resp.status_code == 404


async def test_update_project(client):
    """PATCH /projects/:id should update fields."""
    create_resp = await client.post("/api/v1/projects", json={
        "name": "Before", "project_type": "byor",
    })
    pid = create_resp.json()["id"]
    resp = await client.patch(f"/api/v1/projects/{pid}", json={"name": "After"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "After"
