"""
Pytest configuration and fixtures for cursor-settings-sync tests.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Test data
TEST_SETTINGS = {
    "version": "1.0",
    "platform": "Windows",
    "settings": {
        "editor.fontSize": 14,
        "editor.fontFamily": "Consolas"
    },
    "keybindings": [
        {
            "key": "ctrl+r",
            "command": "workbench.action.reloadWindow"
        }
    ],
    "extensions": [
        {
            "name": "test-extension",
            "version": "1.0.0",
            "publisher": "test-publisher"
        }
    ],
    "snippets": {
        "python": {
            "prefix": "py",
            "body": ["print($1)"]
        }
    }
}

TEST_KEYBINDINGS_CONTENT = """// Empty
[
    {
        "key": "ctrl+r",
        "command": "workbench.action.reloadWindow"
    }
]"""

@pytest.fixture
def mock_settings_file(tmp_path):
    """Create a mock settings.json file."""
    settings_file = tmp_path / "settings.json"
    with open(settings_file, "w") as f:
        json.dump(TEST_SETTINGS["settings"], f)
    return settings_file

@pytest.fixture
def mock_keybindings_file(tmp_path):
    """Create a mock keybindings.json file."""
    keybindings_file = tmp_path / "keybindings.json"
    with open(keybindings_file, "w") as f:
        f.write(TEST_KEYBINDINGS_CONTENT)
    return keybindings_file

@pytest.fixture
def mock_extensions_dir(tmp_path):
    """Create a mock extensions directory with test extensions."""
    extensions_dir = tmp_path / "extensions"
    extensions_dir.mkdir()
    
    # Create extension with package.json
    ext1_dir = extensions_dir / "test-extension-1.0.0"
    ext1_dir.mkdir()
    package_json = ext1_dir / "package.json"
    with open(package_json, "w") as f:
        json.dump({
            "name": "test-extension",
            "version": "1.0.0",
            "publisher": "test-publisher"
        }, f)
    
    # Create extension without package.json
    ext2_dir = extensions_dir / "test-extension-no-package"
    ext2_dir.mkdir()
    
    return extensions_dir

@pytest.fixture
def mock_snippets_dir(tmp_path):
    """Create a mock snippets directory with test snippets."""
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir()
    
    # Create a snippet file
    snippet_file = snippets_dir / "python.json"
    with open(snippet_file, "w") as f:
        json.dump(TEST_SETTINGS["snippets"]["python"], f)
    
    return snippets_dir

@pytest.fixture
def mock_github_token():
    """Set a mock GitHub token for testing."""
    with patch.dict(os.environ, {"GH_TOKEN": "test_token"}):
        yield "test_token"

@pytest.fixture
def mock_gist_response():
    """Create a mock GitHub Gist API response."""
    return {
        "id": "test_gist_id",
        "html_url": "https://gist.github.com/test/test_gist_id",
        "files": {
            "cursor-settings.json": {
                "content": json.dumps(TEST_SETTINGS)
            }
        }
    }
