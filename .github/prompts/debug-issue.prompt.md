---
description: "Debug a failing test, error, or runtime issue"
tools: ["read", "search", "edit", "execute", "read/problems"]
---
# Debug Issue

## Mission
Diagnose and fix the reported issue with minimal, targeted changes.

## Workflow
- Reproduce using the provided command (prefer `uv run ...`).
- Identify root cause (not just symptom).
- Add or adjust tests if appropriate.

## Repo-Specific Focus
- For streaming issues, inspect `DeepResearchAgent.start_research_stream()` and verify:
	- `interaction_id`/`last_event_id` tracking
	- reconnection via `interactions.get(..., last_event_id=...)`
	- terminal event handling (`interaction.complete` / `error`)
- For CLI issues, inspect argument parsing and option interactions (e.g., `--previous-interaction-id` with `--model`).
- Do not print or log secrets; avoid capturing raw prompts or full API payloads in debugging output.

## Validation
- Re-run the failing command and ensure the suite is green.
