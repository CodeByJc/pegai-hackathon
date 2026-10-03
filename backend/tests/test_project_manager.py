"""Tests for ProjectManager."""
import pytest
from pathlib import Path
import tempfile

from app.projects.manager import ProjectManager
from app.models.project import ProjectStatus
from app.core.errors import PyDebugHTTPException


@pytest.fixture
def tmp_manager(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.projects.manager.get_settings",
        lambda: type("S", (), {"workspaces_dir": tmp_path, "max_files_per_project": 20, "max_file_size_bytes": 10**6})(),
    )
    return ProjectManager()


class TestProjectManager:
    def test_create_project(self, tmp_manager):
        meta = tmp_manager.create_project()
        assert meta.project_id.startswith("project_")
        assert meta.status == ProjectStatus.CREATED

    def test_get_project(self, tmp_manager):
        meta = tmp_manager.create_project()
        loaded = tmp_manager.get_project(meta.project_id)
        assert loaded.project_id == meta.project_id

    def test_get_nonexistent_project(self, tmp_manager):
        with pytest.raises(FileNotFoundError):
            tmp_manager.get_project("project_does_not_exist")

    def test_project_exists(self, tmp_manager):
        meta = tmp_manager.create_project()
        assert tmp_manager.project_exists(meta.project_id)
        assert not tmp_manager.project_exists("project_fake")

    def test_add_file(self, tmp_manager):
        meta = tmp_manager.create_project()
        content = b"x = 1\n"
        updated = tmp_manager.add_file(meta.project_id, "main.py", content)
        assert len(updated.files) == 1
        assert updated.files[0].path == "main.py"
        assert updated.status == ProjectStatus.FILES_UPLOADED

    def test_set_traceback_requires_files(self, tmp_manager):
        meta = tmp_manager.create_project()
        with pytest.raises(PyDebugHTTPException) as exc:
            tmp_manager.set_traceback(meta.project_id, "Traceback...")
        assert exc.value.detail["code"] == "FILES_REQUIRED"

    def test_set_traceback(self, tmp_manager):
        meta = tmp_manager.create_project()
        tmp_manager.add_file(meta.project_id, "main.py", b"x=1")
        updated = tmp_manager.set_traceback(meta.project_id, "Traceback (most recent call last):\n  ...")
        assert updated.traceback is not None
        assert updated.status == ProjectStatus.TRACEBACK_SET

    def test_read_original_files(self, tmp_manager):
        meta = tmp_manager.create_project()
        tmp_manager.add_file(meta.project_id, "calc.py", b"def add(a,b): return a+b")
        files = tmp_manager.read_original_files(meta.project_id)
        assert "calc.py" in files
        assert "def add" in files["calc.py"]

    def test_save_and_get_result(self, tmp_manager):
        meta = tmp_manager.create_project()
        report = '{"project_id": "test", "status": "verified"}'
        tmp_manager.save_result(meta.project_id, report)
        loaded = tmp_manager.get_result(meta.project_id)
        assert loaded == report

    def test_original_never_modified(self, tmp_manager):
        meta = tmp_manager.create_project()
        tmp_manager.add_file(meta.project_id, "main.py", b"original = True")
        ws = tmp_manager.get_workspace(meta.project_id)
        ws.reset_working()
        # Modify working copy
        ws.write_working("main.py", b"modified = True")
        # Original must be unchanged
        original_content = ws.read_original("main.py")
        assert original_content == b"original = True"
