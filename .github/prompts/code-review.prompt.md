---
description: "Review recent changes for correctness, security, tests, and style"
tools: ["read", "search", "search/changes", "read/problems"]
---
# Code Review

Review the current change set with a focus on:
- Security: secrets, logging, path handling
- Correctness: streaming and reconnection logic, CLI behavior
- Tests: coverage for critical paths
- Style: Ruff compliance and consistency with existing patterns

## Streaming/Reconnection Checklist
- `interaction_id` set on `interaction.start`
- `last_event_id` updated on events that have `event_id`
- reconnection uses `interactions.get(..., last_event_id=...)`
- terminal events stop processing (`interaction.complete` / `error`)
- backoff/retry behavior remains bounded

## CLI Checklist
- `--previous-interaction-id` behavior is coherent (especially with `--model`)
- error messages are actionable and do not leak sensitive data

Provide feedback grouped as: Critical / Important / Suggestions.
