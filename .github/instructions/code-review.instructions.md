<!-- Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/code-review-generic.instructions.md -->
---
applyTo: "**"
description: "Code review standards for Radiant Filament"
---
# Code Review Guidelines

- Prioritize: security (secrets/input handling) → correctness (stream resume/event ordering) → tests → maintainability.
- Ensure changes keep Ruff clean and maintain current formatting conventions.
- Require tests for bug fixes and for non-trivial logic (especially event handling and CLI parsing).
- Prefer explicit, user-facing errors over silent failures.
- Avoid introducing new dependencies unless clearly justified.

## Comments and Docstrings

- Prefer readable code over extra comments.
- Comments should explain WHY (constraints, invariants, API quirks), not restate the code.
- Docstrings should be short and focused on behavior/contract for public APIs.

## Streaming/Reconnection Checklist

- `interaction_id` is set from `interaction.start`.
- `last_event_id` updates when an event includes `event_id`.
- Reconnect uses `interactions.get(..., last_event_id=...)`.
- Terminal events (`interaction.complete`, `error`) stop processing.
- Backoff/retry behavior remains bounded.

## Repo Workflow

- Verify `uv run ruff check .` and `uv run pytest` succeed for changes affecting behavior.
- Ensure docs are updated when CLI flags or user-visible behavior changes.
