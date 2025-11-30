# Cursor Settings Sync

A CLI tool to sync Cursor settings (extensions, themes, keymaps) across computers using GitHub Gists.

## Features

- Sync Cursor settings, keybindings, and snippets across multiple computers
- Track installed extensions (note: extensions need to be installed manually after sync)
- Uses secret GitHub Gists for secure storage
- Simple push/pull commands for manual synchronization
- Comprehensive unit tests to ensure reliability

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cursor-settings-sync.git
   cd cursor-settings-sync
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Setup

1. Create a GitHub Personal Access Token:
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Click "Generate new token"
   - Give it a name (e.g., "Cursor Settings Sync")
   - Select the "gist" scope
   - Click "Generate token"
   - Copy the token (you won't be able to see it again)

2. Create a `.env` file in the project directory:
   ```bash
   cp .env.example .env
   ```
   
3. Edit the `.env` file and add your GitHub token:
   ```
   GH_TOKEN=your_github_token_here
   ```

## Usage

### Push settings to GitHub Gist

Upload your current Cursor settings to GitHub Gist:

```bash
python main.py push
```

This will collect your settings, keybindings, snippets, and extension list, then upload them to a secret GitHub Gist.

### Pull settings from GitHub Gist

Download and apply settings from GitHub Gist:

```bash
python main.py pull
```

This will download the settings from your GitHub Gist and apply them to your local Cursor installation.

## Testing

The project includes comprehensive unit tests using pytest. To run the tests:

```bash
uv run pytest
```

Or to run tests with verbose output:

```bash
uv run pytest -v
```

## What Gets Synced

- **Settings**: All settings from `settings.json`
- **Keybindings**: Custom keybindings from `keybindings.json`
- **Snippets**: All code snippets from the snippets directory
- **Extensions**: List of installed extensions (names, versions, publishers)

## What Doesn't Get Synced

- Extension files themselves (only the list of extensions is synced)
- Workspace-specific settings
- User-specific themes or custom CSS

## Platform Support

This tool supports:
- Windows
- macOS
- Linux

## Troubleshooting

### "GH_TOKEN environment variable not found"

Make sure you've created a `.env` file with your GitHub token as described in the setup instructions.

### "No existing settings gist found"

This error occurs when trying to pull settings before you've pushed any. Run `python main.py push` first to create the gist.

### Settings not applying correctly

Make sure Cursor is closed before running the pull command to avoid file conflicts.

## Security

- Your settings are stored in a secret GitHub Gist, which means only you can access it with the token
- The GitHub token is stored locally in your `.env` file
- The tool only requests the minimum necessary permissions (gist scope)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite to ensure everything works
6. Submit a pull request

## License

MIT License
