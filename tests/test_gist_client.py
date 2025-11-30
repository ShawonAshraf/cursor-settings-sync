"""
Unit tests for gist_client module.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
import requests
from cursor_sync.gist_client import get_github_token, find_existing_gist, push_to_gist, pull_from_gist
from tests.conftest import TEST_SETTINGS, mock_github_token, mock_gist_response


class TestGetGithubToken:
    """Test cases for get_github_token function."""
    
    @patch.dict('os.environ', {'GH_TOKEN': 'test_token'})
    def test_get_github_token_success(self):
        """Test successful retrieval of GitHub token."""
        token = get_github_token()
        assert token == 'test_token'
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('sys.exit')
    def test_get_github_token_missing(self, mock_exit):
        """Test handling when GitHub token is missing."""
        get_github_token()
        mock_exit.assert_called_once_with(1)


class TestFindExistingGist:
    """Test cases for find_existing_gist function."""
    
    @patch('cursor_sync.gist_client.requests.get')
    def test_find_existing_gist_success(self, mock_get):
        """Test successful finding of existing gist."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "test_gist_id",
                "description": "Cursor Editor Settings Sync"
            },
            {
                "id": "other_gist_id",
                "description": "Other Gist"
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GH_TOKEN': 'test_token'}):
            gist_id = find_existing_gist('test_token')
        
        assert gist_id == "test_gist_id"
    
    @patch('cursor_sync.gist_client.requests.get')
    def test_find_existing_gist_not_found(self, mock_get):
        """Test when no matching gist is found."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "other_gist_id",
                "description": "Other Gist"
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GH_TOKEN': 'test_token'}):
            gist_id = find_existing_gist('test_token')
        
        assert gist_id is None
    
    @patch('cursor_sync.gist_client.requests.get')
    def test_find_existing_gist_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_get.side_effect = Exception("API Error")
        
        with patch.dict('os.environ', {'GH_TOKEN': 'test_token'}):
            gist_id = find_existing_gist('test_token')
        
        assert gist_id is None


class TestPushToGist:
    """Test cases for push_to_gist function."""
    
    @patch('cursor_sync.gist_client.find_existing_gist', return_value=None)
    @patch('cursor_sync.gist_client.requests.post')
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_push_to_gist_create_new(self, mock_token, mock_post, mock_find):
        """Test creating a new gist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "new_gist_id",
            "html_url": "https://gist.github.com/test/new_gist_id"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = push_to_gist(TEST_SETTINGS)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('cursor_sync.gist_client.find_existing_gist', return_value='existing_gist_id')
    @patch('cursor_sync.gist_client.requests.patch')
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_push_to_gist_update_existing(self, mock_token, mock_patch, mock_find):
        """Test updating an existing gist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "existing_gist_id",
            "html_url": "https://gist.github.com/test/existing_gist_id"
        }
        mock_response.raise_for_status.return_value = None
        mock_patch.return_value = mock_response
        
        result = push_to_gist(TEST_SETTINGS)
        
        assert result is True
        mock_patch.assert_called_once()
    
    @patch('cursor_sync.gist_client.requests.post')
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_push_to_gist_api_error(self, mock_token, mock_post):
        """Test handling of API errors during push."""
        mock_post.side_effect = Exception("API Error")
        
        result = push_to_gist(TEST_SETTINGS)
        
        assert result is False


class TestPullFromGist:
    """Test cases for pull_from_gist function."""
    
    @patch('cursor_sync.gist_client.find_existing_gist', return_value='test_gist_id')
    @patch('cursor_sync.gist_client.requests.get')
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_pull_from_gist_success(self, mock_token, mock_get, mock_find):
        """Test successful pulling of settings from gist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "test_gist_id",
            "html_url": "https://gist.github.com/test/test_gist_id",
            "files": {
                "cursor-settings.json": {
                    "content": json.dumps(TEST_SETTINGS)
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        settings = pull_from_gist()
        
        assert settings == TEST_SETTINGS
    
    @patch('cursor_sync.gist_client.find_existing_gist', return_value=None)
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_pull_from_gist_not_found(self, mock_token, mock_find):
        """Test when no gist is found."""
        settings = pull_from_gist()
        
        assert settings is None
    
    @patch('cursor_sync.gist_client.find_existing_gist', return_value='test_gist_id')
    @patch('cursor_sync.gist_client.requests.get')
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_pull_from_gist_file_not_in_gist(self, mock_token, mock_get, mock_find):
        """Test when settings file is not in gist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "test_gist_id",
            "files": {
                "other_file.json": {
                    "content": "{}"
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        settings = pull_from_gist()
        
        assert settings is None
    
    @patch('cursor_sync.gist_client.requests.get')
    @patch('cursor_sync.gist_client.get_github_token', return_value='test_token')
    def test_pull_from_gist_api_error(self, mock_token, mock_get):
        """Test handling of API errors during pull."""
        mock_get.side_effect = Exception("API Error")
        
        settings = pull_from_gist()
        
        assert settings is None
