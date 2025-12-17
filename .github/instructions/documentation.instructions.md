---
applyTo: "README.md,docs/**/*.md,**/*.md"
description: "Documentation standards for Radiant Filament"
---
# Documentation Guidelines

- Keep `README.md` accurate for install/run/lint/test commands.
- When behavior changes (CLI flags, env vars, outputs), update docs in the same change.
- Prefer concise, task-oriented docs (what/why/how) over long narratives.
- Avoid including secrets or real interaction IDs in examples.

## Repo-Specific Notes

- Prefer `uv`-based commands in docs (e.g., `uv sync`, `uv run ...`).
- If streaming/reconnection behavior changes, document user-visible behavior (what happens on disconnect, retries).
- Avoid pasting raw prompts or full unredacted reports into docs.
