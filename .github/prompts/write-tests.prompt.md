---
description: "Write pytest tests for existing or new functionality"
tools: ["read", "search", "edit", "execute", "read/problems"]
---
# Write Tests (pytest)

## Mission
Create or update pytest tests for the specified behavior.

## Workflow
- Identify the public surface to test (CLI parsing, agent event handling, helpers).
- Prefer deterministic tests; do not call the real Gemini API.
- Use fixtures and small focused test cases.

## Agent/Streaming Test Guidance
- Prefer faking the `google.genai` client with `monkeypatch` (or lightweight fakes) to drive sequences of events.
- Include tests for reconnection behavior when relevant:
	- `interaction_id` set on `interaction.start`
	- `last_event_id` updated for each event that has `event_id`
	- reconnection uses `interactions.get(..., last_event_id=...)`
	- terminal events (`interaction.complete` / `error`) stop the loop
- Do not assert on Rich rendering output unless necessary; focus on functional behavior.

## Validation
- Run `uv run pytest` and fix failures.
