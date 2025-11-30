"""
Unit tests for config module.
"""

import pytest
from cursor_sync.config import (
    APP_NAME, VERSION, GIST_FILENAME, GIST_DESCRIPTION,
    GITHUB_API_URL, SETTINGS_FILE, KEYBINDINGS_FILE,
    PACKAGE_JSON_FILE, EXTENSIONS_DIR, SNIPPETS_DIR,
    USER_DIR, LOG_FILE_NAME, LOG_ROTATION_SIZE,
    LOG_RETENTION_DAYS
)


class TestConfig:
    """Test cases for configuration constants."""
    
    def test_app_constants(self):
        """Test application constants."""
        assert APP_NAME == "cursor-settings-sync"
        assert VERSION == "1.0"
    
    def test_gist_constants(self):
        """Test GitHub Gist constants."""
        assert GIST_FILENAME == "cursor-settings.json"
        assert GIST_DESCRIPTION == "Cursor Editor Settings Sync"
        assert GITHUB_API_URL == "https://api.github.com"
    
    def test_file_constants(self):
        """Test file name constants."""
        assert SETTINGS_FILE == "settings.json"
        assert KEYBINDINGS_FILE == "keybindings.json"
        assert PACKAGE_JSON_FILE == "package.json"
    
    def test_directory_constants(self):
        """Test directory name constants."""
        assert EXTENSIONS_DIR == "extensions"
        assert SNIPPETS_DIR == "snippets"
        assert USER_DIR == "User"
    
    def test_log_constants(self):
        """Test logging configuration constants."""
        assert LOG_FILE_NAME == "cursor-sync.log"
        assert LOG_ROTATION_SIZE == "10 MB"
        assert LOG_RETENTION_DAYS == "7 days"
