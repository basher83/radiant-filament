---
description: "Add a new Python module/component consistent with this repo"
tools: ["read", "search", "edit", "read/problems"]
---
# Set Up a New Component

## Mission
Add a new module (or expand an existing one) under `src/radiant_filament/` following current patterns.

## Repo Context
- The core behavior is streaming Gemini Deep Research output with automatic reconnection.
- Keep `DeepResearchAgent.start_research_stream()` semantics stable: event ordering, resume via `interaction_id` + `last_event_id`, and bounded backoff.

## Inputs
- Component name and purpose.
- Where it should live (file path) if not obvious.

## Workflow
- Inspect nearby code for conventions (imports, naming, error handling, Rich usage).
- Create/update the minimal set of files needed.
- Keep functions small and typed where helpful.

## Guardrails
- Do not introduce live network calls in tests.
- Do not log or print secrets; treat `GEMINI_API_KEY` and interaction IDs as sensitive.
- If you add or change CLI options, update `README.md`.

## Quality Checks
- Ensure Ruff formatting/lint rules are satisfied.
- If behavior is non-trivial, add/adjust tests under `tests/`.
