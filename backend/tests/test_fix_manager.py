"""Tests for FixManager."""
import pytest
from pathlib import Path
from app.core.fix_manager import FixManager
from app.core.errors import PyDebugHTTPException
from app.models.diagnosis import FilePatch, FixProposal, GeneratedTestFile
from app.projects.workspace import ProjectWorkspace


@pytest.fixture
def tmp_workspace(tmp_path):
    ws = ProjectWorkspace(tmp_path, "test_project")
    ws.create()
    # Put a source file in original
    ws.write_original("main.py", b"x = 0  # original")
    ws.reset_working()
    return ws


class TestFixManager:
    def setup_method(self):
        self.manager = FixManager()

    def test_apply_fix_modifies_working(self, tmp_workspace):
        fix = FixProposal(
            root_cause="rc",
            description="fix x",
            files_to_modify=[
                FilePatch(path="main.py", description="fix", patch="x = 1  # fixed"),
            ],
        )
        self.manager.apply_fix(tmp_workspace, fix, [])
        working_content = (tmp_workspace.working / "main.py").read_text()
        assert "fixed" in working_content

    def test_apply_fix_does_not_modify_original(self, tmp_workspace):
        fix = FixProposal(
            root_cause="rc",
            description="fix x",
            files_to_modify=[
                FilePatch(path="main.py", description="fix", patch="x = 99"),
            ],
        )
        self.manager.apply_fix(tmp_workspace, fix, [])
        original_content = tmp_workspace.read_original("main.py")
        assert original_content == b"x = 0  # original"

    def test_writes_test_files(self, tmp_workspace):
        fix = FixProposal(root_cause="rc", description="d", files_to_modify=[])
        tests = [GeneratedTestFile(path="tests/test_main.py", content="def test_x(): assert True")]
        self.manager.apply_fix(tmp_workspace, fix, tests)
        test_path = tmp_workspace.working / "tests" / "test_main.py"
        assert test_path.exists()

    def test_rejects_path_traversal_in_fix(self, tmp_workspace):
        fix = FixProposal(
            root_cause="rc",
            description="evil",
            files_to_modify=[
                FilePatch(path="../evil.py", description="evil", patch="import os"),
            ],
        )
        with pytest.raises(PyDebugHTTPException) as exc:
            self.manager.apply_fix(tmp_workspace, fix, [])
        assert exc.value.detail["code"] == "PATH_TRAVERSAL"
