"""
Unit tests for cursor_paths module.
"""

import pytest
from unittest.mock import patch
from cursor_sync.cursor_paths import get_cursor_paths


class TestCursorPaths:
    """Test cases for cursor paths functionality."""
    
    def test_get_cursor_paths_windows(self):
        """Test getting Cursor paths on Windows."""
        with patch('platform.system', return_value='Windows'), \
             patch.dict('os.environ', {
                 'APPDATA': 'C:\\Users\\test\\AppData\\Roaming',
                 'LOCALAPPDATA': 'C:\\Users\\test\\AppData\\Local'
             }):
            paths = get_cursor_paths()
            
            assert paths["settings"] == "C:\\Users\\test\\AppData\\Roaming\\Cursor\\User\\settings.json"
            assert paths["keybindings"] == "C:\\Users\\test\\AppData\\Roaming\\Cursor\\User\\keybindings.json"
            assert paths["extensions"] == "C:\\Users\\test\\AppData\\Local\\Cursor\\extensions"
            assert paths["snippets"] == "C:\\Users\\test\\AppData\\Roaming\\Cursor\\User\\snippets"
    
    def test_get_cursor_paths_macos(self):
        """Test getting Cursor paths on macOS."""
        with patch('platform.system', return_value='Darwin'), \
             patch('pathlib.Path.home', return_value='/Users/test'):
            paths = get_cursor_paths()
            
            assert paths["settings"] == "/Users/test/Library/Application Support/Cursor/User/settings.json"
            assert paths["keybindings"] == "/Users/test/Library/Application Support/Cursor/User/keybindings.json"
            assert paths["extensions"] == "/Users/test/.cursor/extensions"
            assert paths["snippets"] == "/Users/test/Library/Application Support/Cursor/User/snippets"
    
    def test_get_cursor_paths_linux(self):
        """Test getting Cursor paths on Linux."""
        with patch('platform.system', return_value='Linux'), \
             patch('pathlib.Path.home', return_value='/home/test'):
            paths = get_cursor_paths()
            
            assert paths["settings"] == "/home/test/.config/Cursor/User/settings.json"
            assert paths["keybindings"] == "/home/test/.config/Cursor/User/keybindings.json"
            assert paths["extensions"] == "/home/test/.cursor/extensions"
            assert paths["snippets"] == "/home/test/.config/Cursor/User/snippets"
