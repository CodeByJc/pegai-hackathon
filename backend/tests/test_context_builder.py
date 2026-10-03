"""Tests for ContextBuilder."""
import pytest
from app.core.context_builder import ContextBuilder


FILES = {
    "main.py": "from calculator import run\nrun()",
    "calculator.py": "def run():\n    pass",
}
TRACEBACK = 'Traceback (most recent call last):\n  File "calculator.py", line 2, in run\nValueError: bad'


class TestContextBuilder:
    def setup_method(self):
        self.builder = ContextBuilder()

    def test_build_returns_context(self):
        ctx = self.builder.build("proj_test", FILES, TRACEBACK)
        assert ctx.project_id == "proj_test"
        assert ctx.traceback == TRACEBACK

    def test_structure_includes_all_files(self):
        ctx = self.builder.build("proj_test", FILES, TRACEBACK)
        assert "main.py" in ctx.structure_summary
        assert "calculator.py" in ctx.structure_summary

    def test_full_context_includes_source(self):
        ctx = self.builder.build("proj_test", FILES, TRACEBACK)
        assert "def run()" in ctx.full_context
        assert "from calculator import run" in ctx.full_context

    def test_full_context_includes_traceback(self):
        ctx = self.builder.build("proj_test", FILES, TRACEBACK)
        assert "ValueError" in ctx.full_context

    def test_primary_file_inference(self):
        ctx = self.builder.build("proj_test", FILES, TRACEBACK)
        assert ctx.primary_file == "calculator.py"

    def test_empty_files_raises(self):
        with pytest.raises(ValueError, match="No Python files"):
            self.builder.build("proj_test", {}, TRACEBACK)

    def test_empty_traceback_raises(self):
        with pytest.raises(ValueError, match="empty"):
            self.builder.build("proj_test", FILES, "   ")
