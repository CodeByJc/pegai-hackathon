"""
pytest configuration and shared fixtures.
"""
import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def set_test_env(tmp_path, monkeypatch):
    """Force all tests to use a temporary workspaces directory."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("WORKSPACES_DIR", str(tmp_path / "workspaces"))
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    # Reset the settings cache so tmp_path is picked up
    from app.config.settings import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
