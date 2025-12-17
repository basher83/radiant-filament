<!-- Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/python.instructions.md -->
---
applyTo: "**/*.py"
description: "Python conventions for Radiant Filament (uv + ruff + pytest)"
---
# Python Guidelines

- Target Python 3.13+ and keep the codebase modern (no back-compat hacks).
- Follow Ruff formatting and lint settings in `pyproject.toml`.
- Prefer small, testable functions; keep responsibilities narrow.
- Use type hints for new/changed public APIs and for non-trivial internal functions.
- Prefer explicit error types and actionable CLI error messages.
- Avoid unnecessary dependencies; keep the dependency surface small.

## Comments and Docstrings

- Prefer self-explanatory code: better names and smaller functions over comments.
- Write comments only when they explain WHY (constraints, tradeoffs, external API gotchas), not WHAT the code does.
- Avoid redundant or decorative comments.
- Add docstrings for public entry points and non-obvious behavior; keep them concise and behavior-focused.

## Project-Specific Conventions

- Use `uv` for installing/running; avoid raw `pip` instructions.
- Preserve the streaming + reconnection workflow in the agent logic; do not break resume behavior.
- Treat these streaming invariants as stable unless the task explicitly changes them:
	- Yield all API events in the order received.
	- Set `interaction_id` from the `interaction.start` event.
	- Update `last_event_id` whenever an event includes an `event_id`.
	- Resume via `interactions.get(..., last_event_id=last_event_id)`.
	- Treat `interaction.complete` and `error` as terminal.
- Do not print secrets; treat environment variables and identifiers as sensitive.
