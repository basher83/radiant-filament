<!-- Inspired by: https://github.com/github/awesome-copilot/blob/main/instructions/security-and-owasp.instructions.md -->
---
applyTo: "**"
description: "Security guidelines for a CLI that calls external LLM APIs"
---
# Security Guidelines

- Never hardcode secrets (API keys, tokens). Use environment variables.
- Avoid printing secrets or full unredacted API payloads to stdout/stderr.
- Validate and constrain file paths supplied via CLI options (no path traversal).
- Treat user-provided prompts and file contents as untrusted input.
- Prefer safe subprocess patterns; avoid shell=True and unsafe string concatenation.

## Repo-Specific Risks

- Treat `GEMINI_API_KEY`, prompts, interaction IDs, and generated reports as potentially sensitive.
- For file paths (e.g., prompt files, output paths), use safe path handling and clear errors for invalid paths.
