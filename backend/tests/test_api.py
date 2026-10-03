"""Tests for API endpoints (using FastAPI test client)."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Create a TestClient with the workspaces dir redirected to tmp_path.
    conftest.py already sets WORKSPACES_DIR, we just need the client.
    """
    # Re-import app after env is patched (conftest autouse fixture handles env)
    from importlib import import_module, reload
    import app.config.settings as settings_mod
    settings_mod.get_settings.cache_clear()

    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "pydebug-backend"


class TestProjectsAPI:
    def test_create_project(self, client):
        resp = client.post("/api/projects")
        assert resp.status_code == 201
        data = resp.json()
        assert "project_id" in data
        assert data["project_id"].startswith("project_")

    def test_get_nonexistent_project(self, client):
        resp = client.get("/api/projects/project_does_not_exist")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "PROJECT_NOT_FOUND"

    def test_upload_invalid_file_type(self, client):
        # Create project first
        create_resp = client.post("/api/projects")
        pid = create_resp.json()["project_id"]

        # Try uploading a JS file
        resp = client.post(
            f"/api/projects/{pid}/files",
            files={"files": ("script.js", b"console.log('x')", "text/javascript")},
        )
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"

    def test_upload_valid_python_file(self, client):
        create_resp = client.post("/api/projects")
        pid = create_resp.json()["project_id"]
        resp = client.post(
            f"/api/projects/{pid}/files",
            files={"files": ("main.py", b"x = 1", "text/x-python")},
        )
        assert resp.status_code == 200
        assert "main.py" in resp.json()["uploaded"]

    def test_set_traceback_without_files_fails(self, client):
        create_resp = client.post("/api/projects")
        pid = create_resp.json()["project_id"]
        resp = client.post(
            f"/api/projects/{pid}/traceback",
            json={"traceback": "Traceback..."},
        )
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "FILES_REQUIRED"

    def test_set_traceback(self, client):
        create_resp = client.post("/api/projects")
        pid = create_resp.json()["project_id"]
        client.post(
            f"/api/projects/{pid}/files",
            files={"files": ("main.py", b"x=1", "text/x-python")},
        )
        resp = client.post(
            f"/api/projects/{pid}/traceback",
            json={"traceback": "Traceback (most recent):\nKeyError: 'x'"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "traceback_set"

    def test_get_result_before_diagnose(self, client):
        create_resp = client.post("/api/projects")
        pid = create_resp.json()["project_id"]
        resp = client.get(f"/api/projects/{pid}/result")
        assert resp.status_code == 404
