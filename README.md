# Radiant Filament

Radiant Filament is a robust CLI tool designed to interface with Google's Gemini
Deep Research capabilities. It provides a streaming, resilient, and visually
rich terminal interface for conducting deep, agentic research sessions.

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** for dependency management.
- A **Google Gemini API Key** set as an environment variable:

  ```bash
  export GEMINI_API_KEY="your-api-key-here"
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

Run the researcher directly from the CLI:

```bash
uv run radiant-filament "Your research prompt here"
```

### Options

- **Save the report to a file:**

  ```bash
  uv run radiant-filament "Investigate the history of fusion energy" --output report.md
  ```

- **Specify a custom agent version:**
  Use this to connect to a specific model version (defaults to `deep-research-pro-preview-12-2025`).

  ```bash
  uv run radiant-filament "Deep dive into quantum computing" --agent-name "deep-research-pro-preview-12-2025"
  ```

- **View help:**

  ```bash
  uv run radiant-filament --help
  ```

## Features

- **Deep Research**: Leverages Gemini's advanced agentic capabilities to explore complex topics.
- **Resilient Connection**: Built-in automatic reconnection with exponential
  backoff ensures long-running research sessions aren't lost due to transient
  network issues.
- **Rich Terminal UI**: Features real-time Markdown rendering, status spinners,
  and live thought summaries using [Rich](https://github.com/Textualize/rich).
- **Streaming Output**: Watch the research report build in real-time.
