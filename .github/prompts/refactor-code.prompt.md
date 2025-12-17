---
description: "Refactor Python code while preserving behavior and keeping Ruff clean"
tools: ["read", "search", "edit", "execute", "read/problems", "search/changes"]
---
# Refactor Code

## Mission
Refactor the specified area while preserving external behavior and CLI output.

## Guardrails
- Preserve streaming + reconnection semantics.
- Keep these invariants stable unless the task explicitly requires changing them:
	- yield all API events in the order received
	- `interaction_id` is set from `interaction.start`
	- `last_event_id` is updated from each event’s `event_id`
	- resume uses `interactions.get(..., last_event_id=self.last_event_id)`
	- backoff is bounded and retry count is capped
- Preserve CLI-facing error behavior (raise `RuntimeError` for `error` events).
- Do not add logging that could leak `GEMINI_API_KEY`, prompts, or raw API payloads.
- Keep the diff minimal and avoid unrelated formatting churn.

## Validation
- Run `uv run ruff check .` and `uv run pytest`.
