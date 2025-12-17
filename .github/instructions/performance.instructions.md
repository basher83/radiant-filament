<!-- Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/performance-optimization.instructions.md -->
---
applyTo: "**"
description: "Performance guidance (streaming CLI, minimal overhead)"
---
# Performance Guidelines

- Measure before optimizing; prioritize readability unless there is a real bottleneck.
- Avoid extra work in tight streaming loops (string concatenation, repeated parsing, excessive logging).
- Prefer incremental processing for streaming responses; avoid buffering entire payloads unless required.
- Keep retry/backoff logic simple and bounded.

## Streaming CLI Considerations

- Avoid introducing per-event expensive operations (e.g., repeated full-document transforms) in the hot path.
- Keep reconnection retry behavior predictable and bounded to prevent runaway loops.
