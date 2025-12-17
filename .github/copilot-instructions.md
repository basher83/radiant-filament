# GitHub Copilot Instructions (Radiant Filament)

Radiant Filament is a Python 3.13+ CLI that wraps Google Gemini Deep Research with streaming output, reconnection resilience, and a Rich terminal UI.

## Project Defaults

- Use `uv` for dependencies and running commands.
- Keep changes minimal and consistent with existing patterns.
- Run formatting and linting with Ruff, then run tests.

## Quick commands 🔧
- Install deps: `uv sync`
- Run CLI: `uv run radiant-filament "Your prompt"`
- Run tests: `uv run pytest`
- Lint & format: `uv run ruff check .` and `uv run ruff format .`

## Environment & prerequisites
- Python 3.13+ is required.
- `GEMINI_API_KEY` must be set in the environment (see `DeepResearchAgent.__init__`). Example:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Coding Style

- Follow Ruff formatting and lint rules configured in `pyproject.toml` (line length 88, double quotes).
- Prefer clear names and small functions; avoid cleverness.
- Add type hints for new public functions and non-trivial internal APIs.

## Key Files & Architecture Notes

- `src/radiant_filament/main.py` — CLI parsing and validation (see `parse_agent_config`, `validate_file_search_store`).
- `src/radiant_filament/agent.py` — `DeepResearchAgent`: streaming, polling, reconnection logic, and the Rich-based UI.

Important architecture details to preserve:
- Streaming is event-driven: `interaction.start`, `content.delta` (text / thought_summary), `interaction.complete`, `error`.
- Reconnection uses `interaction_id` and `last_event_id` to resume exactly where it left off (exponential backoff, 2s→60s, max retries).
- Background interactions (`background=True`) enable long-running research sessions.

## Security & Privacy

- Never hardcode secrets or credentials.
- Treat `GEMINI_API_KEY` and any interaction IDs / reports as potentially sensitive.
- Avoid logging raw secrets or dumping large unredacted API payloads by default.

## Project-specific conventions & notes 📘
- CLI specifics (see `main.py`):
  - `--file-search` values must start with `fileSearchStores/` (validated by `validate_file_search_store`).
  - `--agent-config` accepts either a JSON string or a path to a JSON file (handled by `parse_agent_config`).
  - `--model` requires `--previous-interaction-id` (validated by CLI).
- Default agent config is defined in `DeepResearchAgent.DEFAULT_AGENT_CONFIG`.
- The streaming generator is `start_research_stream()` — refactors should preserve its event semantics.

## Testing notes ✅
- Tests mock `google.genai.Client` and `interactions.create`/`get` (see `tests/test_agent.py`).
- Typical patterns: use generator functions to simulate streams, raise `ConnectionError` mid-stream, and assert reconnection behavior.
- Speed up tests by monkeypatching `time.sleep`. Use `tmp_path` to test file output paths.
- If you change reconnection or event handling, add tests that simulate transient and permanent errors.

Example test snippets (copy/paste-ready)

1) Mocking a streaming interaction and simulating a mid-stream failure:

```py
from unittest.mock import MagicMock

# Create simple event-like objects (tests use a MockEvent helper)

def stream_1():
    yield MockEvent("interaction.start", restart=True)
    yield MockEvent("content.delta", event_id="1", text="Hello")
    raise ConnectionError("Connection dropped")

def stream_2():
    yield MockEvent("content.delta", event_id="2", text=" World")
    yield MockEvent("interaction.complete")

mock_client = MagicMock()
mock_client.interactions.create.return_value = stream_1()
mock_client.interactions.get.return_value = stream_2()

agent = DeepResearchAgent()
agent.client = mock_client

# Run the streaming generator and assert events are received and reconnection happened
events = list(agent.start_research_stream("test prompt"))
assert len(events) >= 3
mock_client.interactions.create.assert_called_once()
mock_client.interactions.get.assert_called_once()
```

2) Mocking polling and verifying file output (`tmp_path`):

```py
class MockTextOutput:
    def __init__(self, text):
        self.type = "text"
        self.text = text

class MockInteraction:
    def __init__(self, interaction_id, status, outputs=None):
        self.id = interaction_id
        self.status = status
        self.outputs = outputs or []

mock_client = MagicMock()
mock_client.interactions.create.return_value = MockInteraction("id_1", "completed", [MockTextOutput("Done")])

agent = DeepResearchAgent()
agent.client = mock_client

output_file = tmp_path / "output.md"
agent.research_poll("prompt", output_path=str(output_file))
assert output_file.exists()
assert output_file.read_text() == "Done"
```

3) Speeding up tests by stubbing sleep and testing transient errors:

```py
from unittest.mock import MagicMock
monkeypatch.setattr("time.sleep", MagicMock())
# Simulate transient get() error followed by success
mock_client.interactions.get.side_effect = [ConnectionError("transient"), MockInteraction("id", "completed", [MockTextOutput("ok")])]
agent = DeepResearchAgent()
agent.client = mock_client
agent.console = MagicMock()
agent.research_poll("prompt", poll_interval=0)  # runs quickly because sleep is stubbed
```

4) Asserting missing API key behavior:

```py
monkeypatch.delenv("GEMINI_API_KEY", raising=False)
with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
    DeepResearchAgent()
```

Follow existing `tests/test_agent.py` patterns when writing new tests — they provide ready examples for mocking streams and polling behavior.

## Error handling & UI behavior to preserve
- `research()` streams partial output and writes incrementally if `output_path` is provided; it uses Rich `Live` and `Markdown` for UI updates.
- `research_poll()` polls until completion and writes the final report to `output_path` (validates directory/write permissions early).
- Known intermittent error: if error contains "Function call is empty" print a friendly retry tip.

## Dependency Changes

- When adding/removing dependencies, use `uv add` / `uv remove` and ensure `uv.lock` stays consistent.
