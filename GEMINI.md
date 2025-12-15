# Project Context: Radiant Filament

## Overview
A Python-based CLI application that interfaces with the Google Gemini API's "Deep Research" capabilities. It implements a robust client handling streaming interactions, event processing, and automatic reconnection for uninterrupted research sessions.

**Key Technologies:**
- **Language:** Python 3.13+
- **SDK:** `google-genai`
- **Dependency Management:** `uv`
- **Task Runner:** `mise` (optional)
- **Linting/Formatting:** `ruff`

## Architecture
- **`src/radiant_filament/main.py`**: The CLI entry point. Parses command-line arguments (prompt, output file) and initiates the research process.
- **`src/radiant_filament/agent.py`**: Contains the `DeepResearchAgent` class. Manages the API client, handles the event stream (text deltas, thought summaries), and implements a reconnection loop to resume sessions if the connection drops.
- **`pyproject.toml`**: Standard Python configuration file defining dependencies and tool settings.
- **`mise.toml`**: Optional task runner configuration.

## Building and Running

### Prerequisites
- Python 3.13 or higher
- `uv` (Python package installer and runner)
- `GEMINI_API_KEY` environment variable set

### Commands

*   **Run the Agent:**
    ```bash
    uv run radiant-filament "Your research prompt here"

    # Save output to file
    uv run radiant-filament "Your research prompt" --output report.md
    ```

*   **Linting:**
    ```bash
    uv run ruff check .
    ```

*   **Fix Linting Issues:**
    ```bash
    uv run ruff check . --fix
    ```

*   **Formatting:**
    ```bash
    uv run ruff format .
    ```

*   **Run Tests:**
    ```bash
    uv run pytest
    ```

### Alternative: Using mise

If you have `mise` installed, you can use the defined tasks:

```bash
mise run start -- "Your research prompt"
mise run lint
mise run lint-fix
mise run format
```

## Development Conventions

*   **Style Guide:** The project uses `ruff` for both linting and formatting.
    *   Line length: 88 characters (standard Python/Black style).
    *   Quotes: Double quotes.
    *   Indent: Spaces.
*   **Dependency Management:** Always use `uv` for adding or removing dependencies.
    *   `uv add <package>`
*   **Environment:** The project automatically creates a virtual environment in `.venv`.
