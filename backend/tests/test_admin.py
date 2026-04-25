"""Tests for admin endpoints — access control and functionality."""

import pytest
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_admin_stats_forbidden_for_regular_user(client):
    """Non-admin users should get 403."""
    resp = await client.get("/api/v1/admin/stats")
    assert resp.status_code == 403


async def test_admin_users_forbidden_for_regular_user(client):
    """Non-admin users should get 403."""
    resp = await client.get("/api/v1/admin/users")
    assert resp.status_code == 403


async def test_admin_stats_allowed_for_admin(admin_client, db_session):
    """Admin should see stats."""
    # Insert the admin user into DB so COUNT queries work
    from sqlalchemy import text
    await db_session.execute(text(
        "INSERT INTO users (id, email, hashed_password, is_active, role) "
        "VALUES (99, 'admin@ragify.dev', 'x', true, 'admin')"
    ))
    await db_session.commit()

    resp = await admin_client.get("/api/v1/admin/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "total_projects" in data


async def test_admin_list_users(admin_client, db_session):
    """Admin should see user list."""
    from sqlalchemy import text
    await db_session.execute(text(
        "INSERT INTO users (id, email, hashed_password, is_active, role) "
        "VALUES (99, 'admin@ragify.dev', 'x', true, 'admin')"
    ))
    await db_session.commit()

    resp = await admin_client.get("/api/v1/admin/users")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
