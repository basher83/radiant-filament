---
applyTo: "tests/**/*.py,**/test_*.py"
description: "pytest testing standards for Radiant Filament"
---
# Testing Guidelines

- Use `pytest` conventions and keep tests deterministic.
- Prefer unit tests for parsing, event handling, and edge cases; avoid live network calls.
- Use fixtures for shared setup; avoid hidden global state.
- Name tests by behavior and expected outcome.
- Include both happy-path and failure-path coverage for CLI/agent behavior.
- Keep assertions specific and readable.

## Streaming/Reconnection Testing

- Do not call the real Gemini API; fake the `google.genai` client and drive synthetic event sequences.
- Prefer tests that validate invariants rather than terminal UI rendering.
- Prefer asserting behavior/outputs rather than internal comments or verbose log strings.
- For reconnection behavior, test:
	- `interaction_id` is recorded from `interaction.start`.
	- `last_event_id` is updated from each event that includes `event_id`.
	- resume calls `interactions.get(..., last_event_id=...)`.
	- retries are bounded; avoid slow sleeps by monkeypatching time/backoff where needed.
