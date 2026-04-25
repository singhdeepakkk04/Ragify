"""Tests for document upload endpoint."""

import pytest
import io

pytestmark = pytest.mark.asyncio


async def test_upload_unsupported_format(client):
    """Uploading a .exe should be rejected."""
    files = {"file": ("malware.exe", b"\x00\x01\x02\x03", "application/octet-stream")}
    resp = await client.post("/api/v1/documents/upload", files=files, data={"project_id": "1"})
    assert resp.status_code in (400, 404)  # 404 if project doesn't exist, 400 for format


async def test_upload_empty_txt(client):
    """Uploading an empty .txt should be rejected."""
    # First create a project
    proj = await client.post("/api/v1/projects", json={
        "name": "DocTest", "project_type": "byor",
    })
    pid = proj.json()["id"]

    files = {"file": ("empty.txt", b"   ", "text/plain")}
    resp = await client.post("/api/v1/documents/upload", files=files, data={"project_id": str(pid)})
    assert resp.status_code == 400


async def test_upload_mismatched_magic_bytes(client):
    """A file claiming to be .pdf but with wrong magic bytes should be rejected."""
    proj = await client.post("/api/v1/projects", json={
        "name": "MagicTest", "project_type": "byor",
    })
    pid = proj.json()["id"]

    files = {"file": ("fake.pdf", b"this is not a pdf", "application/pdf")}
    resp = await client.post("/api/v1/documents/upload", files=files, data={"project_id": str(pid)})
    assert resp.status_code == 400
    assert "does not match" in resp.json()["detail"]
