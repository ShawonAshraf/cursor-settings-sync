"""
Unit tests for main module.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from main import main
from tests.conftest import TEST_SETTINGS


class TestMain:
    """Test cases for main function."""
    
    @patch('main.collect_settings', return_value=TEST_SETTINGS)
    @patch('main.push_to_gist', return_value=True)
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('sys.argv', ['main.py', 'push'])
    def test_main_push_success(self, mock_parse, mock_push, mock_collect):
        """Test successful push command."""
        mock_args = MagicMock()
        mock_args.command = 'push'
        mock_parse.return_value = mock_args
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()
    
    @patch('main.collect_settings', return_value=TEST_SETTINGS)
    @patch('main.push_to_gist', return_value=False)
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('sys.argv', ['main.py', 'push'])
    def test_main_push_failure(self, mock_parse, mock_push, mock_collect):
        """Test failed push command."""
        mock_args = MagicMock()
        mock_args.command = 'push'
        mock_parse.return_value = mock_args
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
    
    @patch('main.apply_settings', return_value=True)
    @patch('main.pull_from_gist', return_value=TEST_SETTINGS)
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('sys.argv', ['main.py', 'pull'])
    def test_main_pull_success(self, mock_parse, mock_pull, mock_apply):
        """Test successful pull command."""
        mock_args = MagicMock()
        mock_args.command = 'pull'
        mock_parse.return_value = mock_args
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()
    
    @patch('main.apply_settings', return_value=False)
    @patch('main.pull_from_gist', return_value=TEST_SETTINGS)
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('sys.argv', ['main.py', 'pull'])
    def test_main_pull_apply_failure(self, mock_parse, mock_pull, mock_apply):
        """Test pull command with apply failure."""
        mock_args = MagicMock()
        mock_args.command = 'pull'
        mock_parse.return_value = mock_args
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
    
    @patch('main.apply_settings', return_value=True)
    @patch('main.pull_from_gist', return_value=None)
    @patch('main.argparse.ArgumentParser.parse_args')
    @patch('sys.argv', ['main.py', 'pull'])
    def test_main_pull_no_settings(self, mock_parse, mock_pull, mock_apply):
        """Test pull command with no settings found."""
        mock_args = MagicMock()
        mock_args.command = 'pull'
        mock_parse.return_value = mock_args
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
