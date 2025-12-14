# Project Context: Lunar Deep Research (Radiant Filament)

## Overview
This project, internally named "radiant-filament" but located in `lunar-deep-research`, is a Python-based CLI application that interfaces with the Google Gemini API's "Deep Research" capabilities. It implements a robust client handling streaming interactions, event processing, and automatic reconnection for uninterrupted research sessions.

**Key Technologies:**
- **Language:** Python 3.13+
- **SDK:** `google-genai`
- **Dependency Management:** `uv`
- **Task Management:** `mise`
- **Linting/Formatting:** `ruff`

## Architecture
- **`main.py`**: The CLI entry point. It parses command-line arguments (prompt, agent name) and initiates the research process.
- **`agent.py`**: Contains the `DeepResearchAgent` class. This class manages the API client, handles the event stream (text deltas, thought summaries), and implements a reconnection loop to resume sessions if the connection drops.
- **`mise.toml`**: Defines project tasks and environment configuration.
- **`pyproject.toml`**: Standard Python configuration file defining dependencies and tool settings.

## Building and Running

### Prerequisites
- Python 3.13 or higher
- `uv` (Python package installer and runner)
- `mise` (dev tools backend)
- `GEMINI_API_KEY` environment variable set.

### Commands
All tasks are defined in `mise.toml`.

*   **Run the Agent:**
    ```bash
    mise run start -- "Your research prompt here"
    # OR directly with uv
    uv run main.py "Your research prompt here"
    ```

*   **Linting:**
    ```bash
    mise run lint
    ```

*   **Fix Linting Issues:**
    ```bash
    mise run lint-fix
    ```

*   **Formatting:**
    ```bash
    mise run format
    ```

## Development Conventions

*   **Style Guide:** The project uses `ruff` for both linting and formatting.
    *   Line length: 88 characters (standard Python/Black style).
    *   Quotes: Double quotes.
    *   Indent: Spaces.
*   **Dependency Management:** Always use `uv` for adding or removing dependencies.
    *   `uv add <package>`
*   **Task Running:** Prefer using `mise run <task>` to ensure the correct environment and tools are used.
*   **Environment:** The project is configured to automatically create a virtual environment in `.venv`.
