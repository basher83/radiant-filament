# GitHub Copilot Instructions (Radiant Filament)

Radiant Filament is a Python 3.13+ CLI that wraps Google Gemini Deep Research with streaming output, reconnection resilience, and a Rich terminal UI.

## Project Defaults

- Use `uv` for dependencies and running commands.
- Keep changes minimal and consistent with existing patterns.
- Run formatting and linting with Ruff, then run tests.

## Commands

- Install/sync: `uv sync`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Tests: `uv run pytest`

## Coding Style

- Follow Ruff formatting and lint rules configured in `pyproject.toml` (line length 88, double quotes).
- Prefer clear names and small functions; avoid cleverness.
- Add type hints for new public functions and non-trivial internal APIs.

## Architecture Notes

- Streaming/reconnection behavior is core. Preserve event ordering and resume logic when refactoring streaming code.
- Prefer explicit, readable error handling and user-facing messages (this is a CLI).

## Security & Privacy

- Never hardcode secrets or credentials.
- Treat `GEMINI_API_KEY` and any interaction IDs / reports as potentially sensitive.
- Avoid logging raw secrets or dumping large unredacted API payloads by default.

## Dependency Changes

- When adding/removing dependencies, use `uv add` / `uv remove` and ensure `uv.lock` stays consistent.
