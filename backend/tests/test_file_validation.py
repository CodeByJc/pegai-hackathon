"""Tests for file validation."""
import pytest
from app.projects.validator import validate_python_file, validate_file_count
from app.core.errors import PyDebugHTTPException


def make_content(size: int = 100) -> bytes:
    return b"# python file\n" * (size // 14 + 1)


class TestValidatePythonFile:
    def test_valid_py_file(self):
        validate_python_file("main.py", b"print('hello')")

    def test_rejects_js_extension(self):
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("script.js", b"console.log('x')")
        assert exc.value.detail["code"] == "INVALID_FILE_TYPE"

    def test_rejects_exe(self):
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("malware.exe", b"\x00\x00")
        assert exc.value.detail["code"] == "INVALID_FILE_TYPE"

    def test_rejects_no_extension(self):
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("Makefile", b"all:")
        assert exc.value.detail["code"] == "INVALID_FILE_TYPE"

    def test_rejects_path_traversal(self):
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("../etc/passwd.py", b"x=1")
        assert exc.value.detail["code"] == "PATH_TRAVERSAL"

    def test_rejects_absolute_path(self):
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("/etc/shadow.py", b"x=1")
        assert exc.value.detail["code"] == "PATH_TRAVERSAL"

    def test_rejects_oversized_file(self, monkeypatch):
        from app.config import settings as settings_module
        monkeypatch.setattr(
            "app.projects.validator.get_settings",
            lambda: type("S", (), {"max_file_size_bytes": 10, "max_files_per_project": 20})(),
        )
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("big.py", b"x" * 100)
        assert exc.value.detail["code"] == "FILE_TOO_LARGE"

    def test_rejects_invalid_filename_chars(self):
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_python_file("bad;name.py", b"x=1")
        assert exc.value.detail["code"] == "INVALID_FILENAME"


class TestValidateFileCount:
    def test_within_limit(self, monkeypatch):
        monkeypatch.setattr(
            "app.projects.validator.get_settings",
            lambda: type("S", (), {"max_file_size_bytes": 10**6, "max_files_per_project": 5})(),
        )
        # Should not raise
        validate_file_count(current=3, adding=2)

    def test_exceeds_limit(self, monkeypatch):
        monkeypatch.setattr(
            "app.projects.validator.get_settings",
            lambda: type("S", (), {"max_file_size_bytes": 10**6, "max_files_per_project": 5})(),
        )
        with pytest.raises(PyDebugHTTPException) as exc:
            validate_file_count(current=4, adding=2)
        assert exc.value.detail["code"] == "TOO_MANY_FILES"
