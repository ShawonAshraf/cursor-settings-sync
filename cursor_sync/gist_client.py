"""
Gist client module for cursor-settings-sync.

Handles GitHub Gist operations for syncing settings.
"""

import json
import os
import sys
from typing import Dict, Optional
import requests
from dotenv import load_dotenv
from .logger import setup_logging
from .config import GITHUB_API_URL, GIST_FILENAME, GIST_DESCRIPTION

logger = setup_logging()

# Load environment variables
load_dotenv()


def get_github_token() -> str:
    """Get GitHub token from environment variables."""
    token = os.getenv("GH_TOKEN")
    if not token:
        logger.error("GH_TOKEN environment variable not found")
        print("Error: GH_TOKEN environment variable not found.")
        print("Please set GH_TOKEN in your .env file.")
        sys.exit(1)
    return token


def find_existing_gist(token: str) -> Optional[str]:
    """Find an existing gist with description matching our sync gist."""
    logger.debug("Searching for existing settings gist")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(f"{GITHUB_API_URL}/gists", headers=headers)
        response.raise_for_status()
        
        for gist in response.json():
            if gist.get("description") == GIST_DESCRIPTION:
                gist_id = gist["id"]
                logger.info(f"Found existing gist: {gist_id}")
                return gist_id
        logger.info("No existing settings gist found")
    except Exception as e:
        logger.error(f"Error searching for existing gist: {e}")
        print(f"Error searching for existing gist: {e}")
    
    return None


def push_to_gist(settings: Dict) -> bool:
    """Push settings to GitHub Gist."""
    logger.info("Starting to push settings to GitHub Gist")
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
            logger.debug(f"Updating existing gist: {gist_id}")
            response = requests.patch(f"{GITHUB_API_URL}/gists/{gist_id}", headers=headers, json=data)
            print(f"Updating existing gist: {gist_id}")
        else:
            # Create new gist
            logger.debug("Creating new gist")
            response = requests.post(f"{GITHUB_API_URL}/gists", headers=headers, json=data)
            print("Creating new gist")
        
        response.raise_for_status()
        result = response.json()
        gist_url = result['html_url']
        logger.info(f"Successfully pushed settings to gist: {gist_url}")
        print(f"Success! Gist URL: {gist_url}")
        return True
    except Exception as e:
        logger.error(f"Error pushing to gist: {e}")
        print(f"Error pushing to gist: {e}")
        return False


def pull_from_gist() -> Optional[Dict]:
    """Pull settings from GitHub Gist."""
    logger.info("Starting to pull settings from GitHub Gist")
    token = get_github_token()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Find the gist
    gist_id = find_existing_gist(token)
    if not gist_id:
        logger.warning("No existing settings gist found")
        print("No existing settings gist found.")
        return None
    
    try:
        logger.debug(f"Fetching gist: {gist_id}")
        response = requests.get(f"{GITHUB_API_URL}/gists/{gist_id}", headers=headers)
        response.raise_for_status()
        
        gist_data = response.json()
        if GIST_FILENAME in gist_data["files"]:
            content = gist_data["files"][GIST_FILENAME]["content"]
            settings = json.loads(content)
            logger.info("Successfully pulled settings from gist")
            return settings
        else:
            logger.error(f"Settings file {GIST_FILENAME} not found in gist")
            print(f"Settings file {GIST_FILENAME} not found in gist.")
            return None
    except Exception as e:
        logger.error(f"Error pulling from gist: {e}")
        print(f"Error pulling from gist: {e}")
        return None
