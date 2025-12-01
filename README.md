# Cursor Settings Sync

[![Tests](https://github.com/ShawonAshraf/cursor-settings-sync/actions/workflows/tests.yml/badge.svg)](https://github.com/ShawonAshraf/cursor-settings-sync/actions/workflows/tests.yml)

A CLI tool to sync Cursor settings (extensions, themes, keymaps) across computers using GitHub Gists.

## Setup

Generate a GitHub Personal Access Token with the "gist" scope and create a `.env` file with:
```
GH_TOKEN=your_github_token_here
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it installed. Then setup the python env.

```bash
uv sync
source .venv/bin/activate
# or on Windows
.\.venv\Scripts\activate
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
