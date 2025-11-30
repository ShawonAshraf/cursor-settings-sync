"""
Cursor paths module for cursor-settings-sync.

Handles platform-specific paths for Cursor settings.
"""

import os
import platform
from pathlib import Path
from typing import Dict
from .config import SETTINGS_FILE, KEYBINDINGS_FILE, EXTENSIONS_DIR, SNIPPETS_DIR, USER_DIR


def get_cursor_paths() -> Dict[str, str]:
    """Get platform-specific Cursor paths."""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        app_data = os.environ.get("APPDATA", "")
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return {
            "settings": f"{app_data}\\Cursor\\{USER_DIR}\\{SETTINGS_FILE}",
            "keybindings": f"{app_data}\\Cursor\\{USER_DIR}\\{KEYBINDINGS_FILE}",
            "extensions": f"{local_app_data}\\Cursor\\{EXTENSIONS_DIR}",
            "snippets": f"{app_data}\\Cursor\\{USER_DIR}\\{SNIPPETS_DIR}",
        }
    elif system == "Darwin":  # macOS
        return {
            "settings": f"{home}/Library/Application Support/Cursor/{USER_DIR}/{SETTINGS_FILE}",
            "keybindings": f"{home}/Library/Application Support/Cursor/{USER_DIR}/{KEYBINDINGS_FILE}",
            "extensions": f"{home}/.cursor/{EXTENSIONS_DIR}",
            "snippets": f"{home}/Library/Application Support/Cursor/{USER_DIR}/{SNIPPETS_DIR}",
        }
    else:  # Linux
        return {
            "settings": f"{home}/.config/Cursor/{USER_DIR}/{SETTINGS_FILE}",
            "keybindings": f"{home}/.config/Cursor/{USER_DIR}/{KEYBINDINGS_FILE}",
            "extensions": f"{home}/.cursor/{EXTENSIONS_DIR}",
            "snippets": f"{home}/.config/Cursor/{USER_DIR}/{SNIPPETS_DIR}",
        }
