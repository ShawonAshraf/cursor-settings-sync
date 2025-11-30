"""
Unit tests for settings_manager module.
"""

import json
import pytest
from unittest.mock import patch, mock_open
from cursor_sync.settings_manager import collect_settings, apply_settings
from tests.conftest import TEST_SETTINGS, TEST_KEYBINDINGS_CONTENT


class TestCollectSettings:
    """Test cases for collect_settings function."""
    
    def test_collect_settings_success(self):
        """Test successful collection of settings."""
        with patch('cursor_sync.settings_manager.get_cursor_paths') as mock_paths, \
             patch('platform.system', return_value='Windows'), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', new_callable=mock_open, read_data=json.dumps(TEST_SETTINGS["settings"])):
            
            mock_paths.return_value = {
                "settings": "test_settings_path",
                "keybindings": "test_keybindings_path",
                "extensions": "test_extensions_path",
                "snippets": "test_snippets_path"
            }
            
            # Mock the file operations to return empty data for all files except settings
            def mock_open_side_effect(filename, *args, **kwargs):
                if filename == "test_settings_path":
                    return mock_open(read_data=json.dumps(TEST_SETTINGS["settings"]))(filename, *args, **kwargs)
                elif filename == "test_keybindings_path":
                    return mock_open(read_data="[]")(filename, *args, **kwargs)
                else:
                    raise FileNotFoundError(f"File not found: {filename}")
            
            with patch('builtins.open', side_effect=mock_open_side_effect):
                settings = collect_settings()
            
            assert settings["version"] == "1.0"
            assert settings["platform"] == "Windows"
            assert settings["settings"] == TEST_SETTINGS["settings"]
            assert settings["keybindings"] == []
            assert settings["extensions"] == []
            assert settings["snippets"] == {}
    
    @patch('cursor_sync.settings_manager.get_cursor_paths')
    @patch('cursor_sync.settings_manager.platform.system', return_value='Windows')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=TEST_KEYBINDINGS_CONTENT)
    def test_collect_keybindings_with_comments(self, mock_file, mock_exists, mock_paths, mock_platform):
        """Test collecting keybindings with comments."""
        mock_paths.return_value = {
            "settings": "test_settings_path",
            "keybindings": "test_keybindings_path",
            "extensions": "test_extensions_path",
            "snippets": "test_snippets_path"
        }
        
        settings = collect_settings()
        
        assert settings["keybindings"] == [
            {
                "key": "ctrl+r",
                "command": "workbench.action.reloadWindow"
            }
        ]
    
    @patch('cursor_sync.settings_manager.get_cursor_paths')
    @patch('cursor_sync.settings_manager.platform.system', return_value='Windows')
    @patch('os.path.exists', return_value=False)
    def test_collect_settings_file_not_found(self, mock_exists, mock_paths, mock_platform):
        """Test handling when settings files are not found."""
        mock_paths.return_value = {
            "settings": "test_settings_path",
            "keybindings": "test_keybindings_path",
            "extensions": "test_extensions_path",
            "snippets": "test_snippets_path"
        }
        
        settings = collect_settings()
        
        assert settings["settings"] == {}
        assert settings["keybindings"] == {}
        assert settings["extensions"] == []
        assert settings["snippets"] == {}


class TestApplySettings:
    """Test cases for apply_settings function."""
    
    @patch('cursor_sync.settings_manager.get_cursor_paths')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_apply_settings_success(self, mock_file, mock_makedirs, mock_paths):
        """Test successful application of settings."""
        mock_paths.return_value = {
            "settings": "test_settings_path",
            "keybindings": "test_keybindings_path",
            "extensions": "test_extensions_path",
            "snippets": "test_snippets_path"
        }
        
        result = apply_settings(TEST_SETTINGS)
        
        assert result is True
        mock_file.assert_any_call("test_settings_path", "w", encoding="utf-8")
        mock_file.assert_any_call("test_keybindings_path", "w", encoding="utf-8")
    
    @patch('cursor_sync.settings_manager.get_cursor_paths')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_apply_keybindings_with_comment(self, mock_file, mock_makedirs, mock_paths):
        """Test applying keybindings with comment format."""
        mock_paths.return_value = {
            "settings": "test_settings_path",
            "keybindings": "test_keybindings_path",
            "extensions": "test_extensions_path",
            "snippets": "test_snippets_path"
        }
        
        apply_settings(TEST_SETTINGS)
        
        # Check that the file was opened for writing
        mock_file.assert_any_call("test_keybindings_path", "w", encoding="utf-8")
        
        # Get the file handle for keybindings
        handle = mock_file.return_value.__enter__.return_value
        handle.write.assert_any_call("// Empty\n")
    
    @patch('cursor_sync.settings_manager.get_cursor_paths')
    @patch('os.makedirs')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_apply_settings_io_error(self, mock_file, mock_makedirs, mock_paths):
        """Test handling of IO errors when applying settings."""
        mock_paths.return_value = {
            "settings": "test_settings_path",
            "keybindings": "test_keybindings_path",
            "extensions": "test_extensions_path",
            "snippets": "test_snippets_path"
        }
        
        result = apply_settings(TEST_SETTINGS)
        
        assert result is False
