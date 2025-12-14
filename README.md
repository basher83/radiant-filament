# Radiant Filament

A robust CLI tool for deep research using Google Gemini.

## Usage

```bash
uv sync
uv run radiant-filament "Your research prompt" --output report.md
```

## Features

- **Deep Research**: Leverages Gemini's agentic research capabilities.
- **Output Persistence**: Save reports to Markdown files.
- **Rich UI**: Real-time markdown rendering and status updates.
- **Resilient**: Automatic reconnection with exponential backoff.

## Development

### Running Tests

To run the automated test suite:

```bash
uv run pytest
```
