# Radiant Filament

Radiant Filament is a robust CLI tool designed to interface with Google's Gemini Deep Research capabilities. It
provides a streaming, resilient, and visually rich terminal interface for conducting deep, agentic research sessions.

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** for dependency management
- A **Google Gemini API Key** set as an environment variable:

  ```bash
  export GEMINI_API_KEY="your-api-key-here"
  ```

## Quick Start (No Installation)

Run directly from GitHub using `uvx`:

```bash
uvx --from git+https://github.com/basher83/radiant-filament radiant-filament "Your research prompt"
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/basher83/radiant-filament.git
   cd radiant-filament
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

## Usage

Run the researcher from the CLI:

```bash
uv run radiant-filament "Your research prompt here"
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--prompt-file PATH` | Path to a file containing the research prompt |
| `--output PATH` | Save the research report to a file |
| `--agent-name NAME` | Agent version to use (default: `deep-research-pro-preview-12-2025`) |
| `--previous-interaction-id ID` | Continue from a completed interaction for follow-up questions |
| `--model NAME` | Use a model instead of agent for follow-ups (requires `--previous-interaction-id`) |
| `--file-search STORE` | File search store name (can be repeated for multiple stores) |
| `--agent-config JSON` | Agent config as JSON string or path to JSON file |
| `--no-stream` | Use polling mode instead of streaming |

### Examples

Basic research:

```bash
uv run radiant-filament "Research the history of quantum computing"
```

Save output to file:

```bash
uv run radiant-filament "Investigate the history of fusion energy" --output report.md
```

Research using a prompt file:

```bash
uv run radiant-filament --prompt-file docs/prompts/my-research.md --output report.md
```

Specify a custom agent version:

```bash
uv run radiant-filament "Deep dive into quantum computing" --agent-name "deep-research-pro-preview-12-2025"
```

Use polling instead of streaming:

```bash
uv run radiant-filament "Research topic" --no-stream
```

Follow-up on previous research (the interaction ID is printed after each research session):

```bash
uv run radiant-filament "Elaborate on point 2" --previous-interaction-id <id>
```

Quick follow-up with a model (no deep research, faster response):

```bash
uv run radiant-filament "Summarize in 3 bullets" --previous-interaction-id <id> --model gemini-2.5-pro
```

Research with file search (use your uploaded file stores):

```bash
uv run radiant-filament "Analyze our Q1 report" --file-search fileSearchStores/my-store
```

Custom agent configuration:

```bash
uv run radiant-filament "Research topic" --agent-config '{"thinking_summaries": "none"}'
```

Or load config from a file:

```bash
uv run radiant-filament "Research topic" --agent-config config.json
```

View help:

```bash
uv run radiant-filament --help
```

## Features

- **Deep Research**: Leverages Gemini's advanced agentic capabilities to explore complex topics with multi-step
  reasoning.
- **Follow-up Questions**: Continue conversations with previous research sessions using interaction IDs, or use a
  standard model for quick follow-ups.
- **File Search Integration**: Connect to Gemini file search stores to research your own uploaded documents.
- **Streaming & Polling Modes**: Watch results stream in real-time, or use polling mode for more stable connections.
- **Resilient Connection**: Built-in automatic reconnection with exponential backoff (2s to 60s) ensures long-running
  research sessions aren't lost due to transient network issues.
- **Rich Terminal UI**: Features real-time Markdown rendering, status spinners, and live thought summaries using
  [Rich](https://github.com/Textualize/rich).
- **Configurable Agent**: Customize agent behavior via JSON config (inline or file-based).

## Development

Run tests:

```bash
uv run pytest
```

Lint and format:

```bash
uv run ruff check .
uv run ruff format .
```
