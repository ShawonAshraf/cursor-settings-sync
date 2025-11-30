#!/usr/bin/env python3
"""
Cursor Settings Sync CLI

A CLI tool to sync Cursor settings (extensions, themes, keymaps) across computers
using GitHub Gists.
"""

import argparse
import json
import os
import sys
import platform
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
APP_NAME = "cursor-settings-sync"
GIST_FILENAME = "cursor-settings.json"
GIST_DESCRIPTION = "Cursor Editor Settings Sync"

# Platform-specific paths
def get_cursor_paths() -> Dict[str, str]:
    """Get platform-specific Cursor paths."""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        app_data = os.environ.get("APPDATA", "")
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return {
            "settings": f"{app_data}\\Cursor\\User\\settings.json",
            "keybindings": f"{app_data}\\Cursor\\User\\keybindings.json",
            "extensions": f"{local_app_data}\\Cursor\\extensions",
            "snippets": f"{app_data}\\Cursor\\User\\snippets",
        }
    elif system == "Darwin":  # macOS
        return {
            "settings": f"{home}/Library/Application Support/Cursor/User/settings.json",
            "keybindings": f"{home}/Library/Application Support/Cursor/User/keybindings.json",
            "extensions": f"{home}/.cursor/extensions",
            "snippets": f"{home}/Library/Application Support/Cursor/User/snippets",
        }
    else:  # Linux
        return {
            "settings": f"{home}/.config/Cursor/User/settings.json",
            "keybindings": f"{home}/.config/Cursor/User/keybindings.json",
            "extensions": f"{home}/.cursor/extensions",
            "snippets": f"{home}/.config/Cursor/User/snippets",
        }

def get_github_token() -> str:
    """Get GitHub token from environment variables."""
    token = os.getenv("GH_TOKEN")
    if not token:
        print("Error: GH_TOKEN environment variable not found.")
        print("Please set GH_TOKEN in your .env file.")
        sys.exit(1)
    return token

def collect_settings() -> Dict:
    """Collect all Cursor settings from the local system."""
    paths = get_cursor_paths()
    settings = {
        "version": "1.0",
        "platform": platform.system(),
        "settings": {},
        "keybindings": {},
        "extensions": [],
        "snippets": {},
    }
    
    # Collect settings.json
    if os.path.exists(paths["settings"]):
        try:
            with open(paths["settings"], "r", encoding="utf-8") as f:
                settings["settings"] = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read settings file: {e}")
    
    # Collect keybindings.json
    if os.path.exists(paths["keybindings"]):
        try:
            with open(paths["keybindings"], "r", encoding="utf-8") as f:
                content = f.read()
                # Remove JSON comments (lines starting with //)
                lines = content.split('\n')
                cleaned_lines = [line for line in lines if not line.strip().startswith('//')]
                cleaned_content = '\n'.join(cleaned_lines)
                # Parse the cleaned JSON
                if cleaned_content.strip():  # Check if there's content after removing comments
                    settings["keybindings"] = json.loads(cleaned_content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read keybindings file: {e}")
    
    # Collect extensions list
    if os.path.exists(paths["extensions"]):
        try:
            extensions_dir = Path(paths["extensions"])
            for ext_dir in extensions_dir.iterdir():
                if ext_dir.is_dir():
                    # Extract extension name from directory
                    ext_name = ext_dir.name
                    # Try to get package.json for more details
                    package_json = ext_dir / "package.json"
                    if package_json.exists():
                        try:
                            with open(package_json, "r", encoding="utf-8") as f:
                                package_data = json.load(f)
                                ext_info = {
                                    "name": package_data.get("name", ext_name),
                                    "version": package_data.get("version", "unknown"),
                                    "publisher": package_data.get("publisher", "unknown"),
                                }
                                settings["extensions"].append(ext_info)
                        except (json.JSONDecodeError, IOError):
                            settings["extensions"].append({"name": ext_name})
                    else:
                        settings["extensions"].append({"name": ext_name})
        except Exception as e:
            print(f"Warning: Could not read extensions directory: {e}")
    
    # Collect snippets
    if os.path.exists(paths["snippets"]):
        try:
            snippets_dir = Path(paths["snippets"])
            for snippet_file in snippets_dir.glob("*.json"):
                try:
                    with open(snippet_file, "r", encoding="utf-8") as f:
                        snippet_name = snippet_file.stem
                        settings["snippets"][snippet_name] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not read snippet file {snippet_file}: {e}")
        except Exception as e:
            print(f"Warning: Could not read snippets directory: {e}")
    
    return settings

def find_existing_gist(token: str) -> Optional[str]:
    """Find an existing gist with the description matching our sync gist."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get("https://api.github.com/gists", headers=headers)
        response.raise_for_status()
        
        for gist in response.json():
            if gist.get("description") == GIST_DESCRIPTION:
                return gist["id"]
    except Exception as e:
        print(f"Error searching for existing gist: {e}")
    
    return None

def push_to_gist(settings: Dict) -> bool:
    """Push settings to GitHub Gist."""
    token = get_github_token()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if gist already exists
    gist_id = find_existing_gist(token)
    
    data = {
        "description": GIST_DESCRIPTION,
        "public": False,
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(settings, indent=2)
            }
        }
    }
    
    try:
        if gist_id:
            # Update existing gist
            response = requests.patch(f"https://api.github.com/gists/{gist_id}", headers=headers, json=data)
            print(f"Updating existing gist: {gist_id}")
        else:
            # Create new gist
            response = requests.post("https://api.github.com/gists", headers=headers, json=data)
            print("Creating new gist")
        
        response.raise_for_status()
        result = response.json()
        print(f"Success! Gist URL: {result['html_url']}")
        return True
    except Exception as e:
        print(f"Error pushing to gist: {e}")
        return False

def pull_from_gist() -> Optional[Dict]:
    """Pull settings from GitHub Gist."""
    token = get_github_token()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Find the gist
    gist_id = find_existing_gist(token)
    if not gist_id:
        print("No existing settings gist found.")
        return None
    
    try:
        response = requests.get(f"https://api.github.com/gists/{gist_id}", headers=headers)
        response.raise_for_status()
        
        gist_data = response.json()
        if GIST_FILENAME in gist_data["files"]:
            content = gist_data["files"][GIST_FILENAME]["content"]
            return json.loads(content)
        else:
            print(f"Settings file {GIST_FILENAME} not found in gist.")
            return None
    except Exception as e:
        print(f"Error pulling from gist: {e}")
        return None

def apply_settings(settings: Dict) -> bool:
    """Apply pulled settings to the local system."""
    paths = get_cursor_paths()
    success = True
    
    # Create directories if they don't exist
    for path_key in ["settings", "keybindings", "snippets"]:
        dir_path = os.path.dirname(paths[path_key])
        os.makedirs(dir_path, exist_ok=True)
    
    # Apply settings.json
    if settings.get("settings"):
        try:
            with open(paths["settings"], "w", encoding="utf-8") as f:
                json.dump(settings["settings"], f, indent=2)
            print(f"Updated settings file: {paths['settings']}")
        except IOError as e:
            print(f"Error writing settings file: {e}")
            success = False
    
    # Apply keybindings.json
    if settings.get("keybindings"):
        try:
            with open(paths["keybindings"], "w", encoding="utf-8") as f:
                # Write with comment format similar to Cursor's default
                f.write("// Empty\n")
                json.dump(settings["keybindings"], f, indent=2)
            print(f"Updated keybindings file: {paths['keybindings']}")
        except IOError as e:
            print(f"Error writing keybindings file: {e}")
            success = False
    
    # Apply snippets
    if settings.get("snippets"):
        snippets_dir = Path(paths["snippets"])
        snippets_dir.mkdir(exist_ok=True, parents=True)
        
        for snippet_name, snippet_content in settings["snippets"].items():
            try:
                snippet_file = snippets_dir / f"{snippet_name}.json"
                with open(snippet_file, "w", encoding="utf-8") as f:
                    json.dump(snippet_content, f, indent=2)
                print(f"Updated snippet: {snippet_file}")
            except IOError as e:
                print(f"Error writing snippet file {snippet_name}: {e}")
                success = False
    
    # Note: We don't automatically install extensions as that would require
    # additional API calls to Cursor. We just list what extensions were synced.
    if settings.get("extensions"):
        print("\nExtensions found in sync:")
        for ext in settings["extensions"]:
            print(f"  - {ext.get('publisher', 'unknown')}.{ext.get('name', 'unknown')} (v{ext.get('version', 'unknown')})")
        print("\nNote: Extensions need to be installed manually in Cursor.")
    
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Sync Cursor settings across computers using GitHub Gists"
    )
    parser.add_argument(
        "command",
        choices=["push", "pull"],
        help="Command to execute: 'push' to upload settings, 'pull' to download settings"
    )
    
    args = parser.parse_args()
    
    if args.command == "push":
        print("Collecting Cursor settings...")
        settings = collect_settings()
        if push_to_gist(settings):
            print("Settings successfully pushed to GitHub Gist!")
        else:
            print("Failed to push settings to GitHub Gist.")
            sys.exit(1)
    
    elif args.command == "pull":
        print("Pulling settings from GitHub Gist...")
        settings = pull_from_gist()
        if settings:
            if apply_settings(settings):
                print("Settings successfully applied!")
            else:
                print("Some settings could not be applied.")
                sys.exit(1)
        else:
            print("No settings found or failed to pull from GitHub Gist.")
            sys.exit(1)


if __name__ == "__main__":
    main()
