"""Integration tests for /api/v1/projects — requires DB + Redis."""
import pytest
from httpx import AsyncClient
from app.models.user import User
from tests.conftest import make_auth_header

@pytest.mark.integration
class TestCreateProject:
    async def test_create_success(self, client: AsyncClient, test_user: User):
        r = await client.post("/api/v1/projects", json={"name": "Test", "project_type": "qa"}, headers=make_auth_header(test_user))
        assert r.status_code == 200
        assert r.json()["owner_id"] == test_user.id

    async def test_create_unauthenticated(self, client: AsyncClient):
        r = await client.post("/api/v1/projects", json={"name": "Test"})
        assert r.status_code == 401

@pytest.mark.integration
class TestOwnershipIsolation:
    async def test_user_cannot_access_others_project(self, client: AsyncClient, test_user: User, admin_user: User):
        r = await client.post("/api/v1/projects", json={"name": "Admin Project", "project_type": "qa"}, headers=make_auth_header(admin_user))
        pid = r.json()["id"]
        r2 = await client.get(f"/api/v1/projects/{pid}", headers=make_auth_header(test_user))
        assert r2.status_code == 404

    async def test_user_cannot_delete_others_project(self, client: AsyncClient, test_user: User, admin_user: User):
        r = await client.post("/api/v1/projects", json={"name": "Target", "project_type": "qa"}, headers=make_auth_header(admin_user))
        pid = r.json()["id"]
        r2 = await client.delete(f"/api/v1/projects/{pid}", headers=make_auth_header(test_user))
        assert r2.status_code == 404
