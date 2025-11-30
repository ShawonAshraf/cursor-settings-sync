"""
Cursor Settings Sync package.

A CLI tool to sync Cursor settings (extensions, themes, keymaps) across computers
using GitHub Gists.
"""

from .settings_manager import collect_settings, apply_settings
from .gist_client import push_to_gist, pull_from_gist

__all__ = ["collect_settings", "apply_settings", "push_to_gist", "pull_from_gist"]
