"""
Settings manager module for cursor-settings-sync.

Handles collecting and applying Cursor settings.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict
from .logger import setup_logging
from .cursor_paths import get_cursor_paths
from .config import VERSION, PACKAGE_JSON_FILE

logger = setup_logging()


def collect_settings() -> Dict:
    """Collect all Cursor settings from the local system."""
    logger.info("Starting to collect Cursor settings")
    paths = get_cursor_paths()
    logger.debug(f"Cursor paths: {paths}")
    
    settings = {
        "version": VERSION,
        "platform": platform.system(),
        "settings": {},
        "keybindings": {},
        "extensions": [],
        "snippets": {},
    }
    
    # Collect settings.json
    if os.path.exists(paths["settings"]):
        logger.debug(f"Reading settings from {paths['settings']}")
        try:
            with open(paths["settings"], "r", encoding="utf-8") as f:
                settings["settings"] = json.load(f)
            logger.info("Successfully loaded settings.json")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not read settings file: {e}")
            print(f"Warning: Could not read settings file: {e}")
    else:
        logger.warning(f"Settings file not found at {paths['settings']}")
    
    # Collect keybindings.json
    if os.path.exists(paths["keybindings"]):
        logger.debug(f"Reading keybindings from {paths['keybindings']}")
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
                    logger.info("Successfully loaded keybindings.json")
                else:
                    logger.info("Keybindings file is empty after removing comments")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not read keybindings file: {e}")
            print(f"Warning: Could not read keybindings file: {e}")
    else:
        logger.warning(f"Keybindings file not found at {paths['keybindings']}")
    
    # Collect extensions list
    if os.path.exists(paths["extensions"]):
        logger.debug(f"Scanning extensions directory: {paths['extensions']}")
        try:
            extensions_dir = Path(paths["extensions"])
            for ext_dir in extensions_dir.iterdir():
                if ext_dir.is_dir():
                    # Extract extension name from directory
                    ext_name = ext_dir.name
                    # Try to get package.json for more details
                    package_json = ext_dir / PACKAGE_JSON_FILE
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
                                logger.debug(f"Found extension: {ext_info.get('publisher', 'unknown')}.{ext_info.get('name', 'unknown')}")
                        except (json.JSONDecodeError, IOError):
                            settings["extensions"].append({"name": ext_name})
                            logger.debug(f"Found extension (no package.json): {ext_name}")
                    else:
                        settings["extensions"].append({"name": ext_name})
                        logger.debug(f"Found extension (no package.json): {ext_name}")
            logger.info(f"Found {len(settings['extensions'])} extensions")
        except Exception as e:
            logger.error(f"Could not read extensions directory: {e}")
            print(f"Warning: Could not read extensions directory: {e}")
    else:
        logger.warning(f"Extensions directory not found at {paths['extensions']}")
    
    # Collect snippets
    if os.path.exists(paths["snippets"]):
        logger.debug(f"Scanning snippets directory: {paths['snippets']}")
        try:
            snippets_dir = Path(paths["snippets"])
            for snippet_file in snippets_dir.glob("*.json"):
                try:
                    with open(snippet_file, "r", encoding="utf-8") as f:
                        snippet_name = snippet_file.stem
                        settings["snippets"][snippet_name] = json.load(f)
                        logger.debug(f"Found snippet: {snippet_name}")
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not read snippet file {snippet_file}: {e}")
                    print(f"Warning: Could not read snippet file {snippet_file}: {e}")
            logger.info(f"Found {len(settings['snippets'])} snippet files")
        except Exception as e:
            logger.error(f"Could not read snippets directory: {e}")
            print(f"Warning: Could not read snippets directory: {e}")
    else:
        logger.warning(f"Snippets directory not found at {paths['snippets']}")
    
    logger.info("Finished collecting Cursor settings")
    return settings


def apply_settings(settings: Dict) -> bool:
    """Apply pulled settings to the local system."""
    logger.info("Starting to apply settings to local system")
    paths = get_cursor_paths()
    logger.debug(f"Target paths: {paths}")
    success = True
    
    # Create directories if they don't exist
    for path_key in ["settings", "keybindings", "snippets"]:
        dir_path = os.path.dirname(paths[path_key])
        logger.debug(f"Ensuring directory exists: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)
    
    # Apply settings.json
    if settings.get("settings"):
        logger.debug(f"Applying settings to {paths['settings']}")
        try:
            with open(paths["settings"], "w", encoding="utf-8") as f:
                json.dump(settings["settings"], f, indent=2)
            logger.info(f"Updated settings file: {paths['settings']}")
            print(f"Updated settings file: {paths['settings']}")
        except IOError as e:
            logger.error(f"Error writing settings file: {e}")
            print(f"Error writing settings file: {e}")
            success = False
    
    # Apply keybindings.json
    if settings.get("keybindings"):
        logger.debug(f"Applying keybindings to {paths['keybindings']}")
        try:
            with open(paths["keybindings"], "w", encoding="utf-8") as f:
                # Write with comment format similar to Cursor's default
                f.write("// Empty\n")
                json.dump(settings["keybindings"], f, indent=2)
            logger.info(f"Updated keybindings file: {paths['keybindings']}")
            print(f"Updated keybindings file: {paths['keybindings']}")
        except IOError as e:
            logger.error(f"Error writing keybindings file: {e}")
            print(f"Error writing keybindings file: {e}")
            success = False
    
    # Apply snippets
    if settings.get("snippets"):
        logger.debug(f"Applying {len(settings['snippets'])} snippets")
        snippets_dir = Path(paths["snippets"])
        snippets_dir.mkdir(exist_ok=True, parents=True)
        
        for snippet_name, snippet_content in settings["snippets"].items():
            try:
                snippet_file = snippets_dir / f"{snippet_name}.json"
                with open(snippet_file, "w", encoding="utf-8") as f:
                    json.dump(snippet_content, f, indent=2)
                logger.debug(f"Updated snippet: {snippet_file}")
                print(f"Updated snippet: {snippet_file}")
            except IOError as e:
                logger.error(f"Error writing snippet file {snippet_name}: {e}")
                print(f"Error writing snippet file {snippet_name}: {e}")
                success = False
        logger.info(f"Applied {len(settings['snippets'])} snippet files")
    
    # Note: We don't automatically install extensions as that would require
    # additional API calls to Cursor. We just list what extensions were synced.
    if settings.get("extensions"):
        logger.info(f"Found {len(settings['extensions'])} extensions in sync")
        print("\nExtensions found in sync:")
        for ext in settings["extensions"]:
            print(f"  - {ext.get('publisher', 'unknown')}.{ext.get('name', 'unknown')} (v{ext.get('version', 'unknown')})")
        print("\nNote: Extensions need to be installed manually in Cursor.")
    
    if success:
        logger.info("Successfully applied all settings")
    else:
        logger.warning("Some settings could not be applied")
    
    return success
