# Cursor Settings Sync

A CLI tool to sync Cursor settings (extensions, themes, keymaps) across computers using GitHub Gists.

## Setup

Generate a GitHub Personal Access Token with the "gist" scope and create a `.env` file with:
```
GH_TOKEN=your_github_token_here
```

## Usage

Run the project with uv:

```bash
uv run python main.py push  # Upload settings to GitHub Gist
uv run python main.py pull  # Download settings from GitHub Gist
```

## Testing

Run tests with:

```bash
uv run pytest
```
