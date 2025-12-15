# Radiant Filament

A CLI tool for Google Gemini Deep Research with streaming, reconnection resilience, and rich terminal output.

## Quick Reference

```bash
# Run research
uv run radiant-filament "Your research prompt"

# Save output to file
uv run radiant-filament "Your prompt" --output report.md

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
src/radiant_filament/
  main.py       # CLI entrypoint, argument parsing
  agent.py      # DeepResearchAgent class, streaming logic, reconnection handling
```

## Architecture

The codebase centers on `DeepResearchAgent` which wraps the `google-genai` client. Key design decisions:

- Streaming with automatic reconnection using exponential backoff (2s to 60s max)
- Background interactions via `interactions.create(background=True)` to enable long-running research
- Event-driven processing: `interaction.start`, `content.delta`, `interaction.complete`, `error`
- Rich terminal UI with live Markdown rendering and status spinners

## Code Style

- Python 3.13+, managed with `uv`
- Ruff for linting (E, F, I, B, UP rules) and formatting
- Line length 88, double quotes, space indent
- No backwards compatibility; fix-forward approach

## Environment

Requires `GEMINI_API_KEY` environment variable.

## Key Patterns

- Generator-based streaming in `start_research_stream()` yields all API events
- Reconnection state tracked via `interaction_id` and `last_event_id`
- UI updates through Rich's `Live` context manager with `generate_view()` closure
