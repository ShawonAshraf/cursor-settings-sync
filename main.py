#!/usr/bin/env python3
"""
Cursor Settings Sync CLI

A CLI tool to sync Cursor settings (extensions, themes, keymaps) across computers
using GitHub Gists.
"""

import argparse
import sys
from cursor_sync import collect_settings, apply_settings, push_to_gist, pull_from_gist
from cursor_sync.logger import setup_logging

# Set up logging
logger = setup_logging()


def main():
    logger.info("Starting cursor-settings-sync CLI")
    parser = argparse.ArgumentParser(
        description="Sync Cursor settings across computers using GitHub Gists"
    )
    parser.add_argument(
        "command",
        choices=["push", "pull"],
        help="Command to execute: 'push' to upload settings, 'pull' to download settings"
    )
    
    args = parser.parse_args()
    logger.info(f"Executing command: {args.command}")
    
    if args.command == "push":
        print("Collecting Cursor settings...")
        settings = collect_settings()
        if push_to_gist(settings):
            logger.info("Settings successfully pushed to GitHub Gist")
            print("Settings successfully pushed to GitHub Gist!")
        else:
            logger.error("Failed to push settings to GitHub Gist")
            print("Failed to push settings to GitHub Gist.")
            sys.exit(1)
    
    elif args.command == "pull":
        print("Pulling settings from GitHub Gist...")
        settings = pull_from_gist()
        if settings:
            if apply_settings(settings):
                logger.info("Settings successfully applied")
                print("Settings successfully applied!")
            else:
                logger.warning("Some settings could not be applied")
                print("Some settings could not be applied.")
                sys.exit(1)
        else:
            logger.error("No settings found or failed to pull from GitHub Gist")
            print("No settings found or failed to pull from GitHub Gist.")
            sys.exit(1)
    
    logger.info("cursor-settings-sync CLI completed successfully")


if __name__ == "__main__":
    main()
