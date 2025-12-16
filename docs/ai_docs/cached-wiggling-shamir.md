# Plan: Fix PR Review Issues (Round 2)

## Overview
Address 15 issues from the follow-up PR review (7 important + 8 suggestions).

**Previous round (17 issues) - COMPLETED ✅**

## Files to Modify
- `src/radiant_filament/agent.py` - Docstrings, early validation
- `src/radiant_filament/main.py` - Docstrings
- `tests/test_agent.py` - New tests for edge cases
- `tests/test_main.py` - CLI integration tests (optional)

---

## Phase 1: Important Issues (7)

### 1.1 Silent return on timeout in research_poll()
**Location:** `agent.py:299-304`
**Severity:** HIGH

**Problem:** Timeout prints error but returns silently - callers can't detect failure programmatically.

**Fix:** Raise `TimeoutError` after printing message.

```python
if poll_count >= max_polls:
    timeout_msg = f"Research timed out after {poll_count * poll_interval}s"
    self.console.print(f"[bold red]{timeout_msg}[/bold red]")
    raise TimeoutError(timeout_msg)
```

### 1.2 Silent returns for failed/cancelled/requires_action
**Location:** `agent.py:327-341`
**Severity:** HIGH

**Problem:** Failure states print but return silently - programmatic callers can't distinguish success from failure.

**Fix:** Raise `RuntimeError` for each failure state.

```python
if current_status == "requires_action":
    msg = f"Research requires action. Interaction ID: {self.interaction_id}"
    self.console.print(f"[yellow]{msg}[/yellow]")
    raise RuntimeError(msg)

if current_status == "failed":
    error_msg = getattr(interaction, "error", None) or "Unknown error"
    self.console.print(f"[bold red]Research failed: {error_msg}[/bold red]")
    raise RuntimeError(f"Research failed: {error_msg}")

if current_status == "cancelled":
    self.console.print("[yellow]Research was cancelled.[/yellow]")
    raise RuntimeError("Research was cancelled")
```

### 1.3 File write failure doesn't propagate
**Location:** `agent.py:356-366`
**Severity:** MEDIUM

**Problem:** File save errors in `research_poll()` are printed but not raised, inconsistent with `research()`.

**Fix:** Raise exception after printing error.

```python
except OSError as e:
    self.console.print(f"[bold red]Failed to save report: {e}[/bold red]")
    raise RuntimeError(f"Failed to save report to '{output_path}': {e}") from e
```

### 1.4 No output received returns silently
**Location:** `agent.py:367-372`
**Severity:** MEDIUM

**Problem:** Completed with no output prints warning but returns silently.

**Fix:** Raise exception for unexpected empty output.

```python
else:
    msg = "Research completed but no text output was received"
    self.console.print(f"[yellow]{msg}[/yellow]")
    raise RuntimeError(msg)
```

### 1.5 Missing API key validation test
**Location:** `tests/test_agent.py`
**Severity:** CRITICAL GAP

**Fix:** Add test for missing API key.

```python
def test_missing_api_key_raises_value_error(monkeypatch):
    """Test that missing GEMINI_API_KEY raises descriptive ValueError."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
        DeepResearchAgent()
```

### 1.6 Missing max retries test
**Location:** `tests/test_agent.py`
**Severity:** CRITICAL GAP

**Fix:** Add test for reconnection exhaustion.

```python
def test_stream_raises_after_max_retries(monkeypatch):
    """Test reconnection gives up after max_retries and raises RuntimeError."""
    mock_client = MagicMock()

    def stream_1():
        yield MockEvent("interaction.start", restart=True)
        raise Exception("Connection dropped")

    mock_client.interactions.create.return_value = stream_1()
    mock_client.interactions.get.side_effect = Exception("Network error")

    agent = DeepResearchAgent()
    agent.client = mock_client
    agent.console = MagicMock()
    monkeypatch.setattr("time.sleep", MagicMock())

    with pytest.raises(RuntimeError, match="Failed to reconnect after 10 attempts"):
        list(agent.start_research_stream("test prompt"))
```

### 1.7 Missing poll timeout test
**Location:** `tests/test_agent.py`
**Severity:** HIGH GAP

**Fix:** Add test for polling timeout (requires patching max_polls).

```python
def test_poll_times_out_after_max_polls(monkeypatch):
    """Test that research_poll raises TimeoutError after max_polls."""
    # Will need to test by checking timeout message is printed
    # since max_polls is hardcoded
```

---

## Phase 2: Suggestions (8)

### 2.1 Fix docstrings - remove "CLI enforces" reference
**Location:** `agent.py:50-51, 160-161, 249-250`

**Fix:** Change docstrings to describe method behavior, not CLI behavior.

```python
# From:
model: Use a model instead of agent (CLI enforces this requires
    previous_interaction_id).

# To:
model: Use a model instead of agent. When provided, agent_config is
    ignored. Typically used with previous_interaction_id for follow-ups.
```

### 2.2 Add Args/Returns to _merge_agent_config()
**Location:** `agent.py:28-29`

```python
def _merge_agent_config(self, user_config):
    """Merge user config with defaults. User values override defaults.

    Args:
        user_config: Optional dict of config overrides. If None, returns defaults.

    Returns:
        dict: Merged configuration with DEFAULT_AGENT_CONFIG as base.
    """
```

### 2.3 Add Args/Returns/Raises to parse_agent_config()
**Location:** `main.py:9-10`

```python
def parse_agent_config(value):
    """Parse agent config from JSON string or file path.

    Args:
        value: JSON string, path to JSON file, or None.

    Returns:
        dict or None: Parsed config dict, or None if value is None.

    Raises:
        argparse.ArgumentTypeError: If JSON is invalid or file cannot be read.
    """
```

### 2.4 Add Args/Returns/Raises to validate_file_search_store()
**Location:** `main.py:33-34`

```python
def validate_file_search_store(value):
    """Validate file search store name format.

    Args:
        value: Store name string to validate.

    Returns:
        str: The validated store name (unchanged if valid).

    Raises:
        argparse.ArgumentTypeError: If store name doesn't start with 'fileSearchStores/'.
    """
```

### 2.5 Add test for requires_action status
**Location:** `tests/test_agent.py`

```python
def test_poll_raises_on_requires_action(monkeypatch):
    """Test that research_poll raises RuntimeError on requires_action status."""
    mock_client = MagicMock()
    mock_interaction = MockInteraction("test_123", "requires_action")
    mock_client.interactions.create.return_value = mock_interaction

    agent = DeepResearchAgent()
    agent.client = mock_client
    agent.console = MagicMock()

    with pytest.raises(RuntimeError, match="requires action"):
        agent.research_poll("test prompt")
```

### 2.6 Add test for poll error recovery
**Location:** `tests/test_agent.py`

```python
def test_poll_recovers_from_transient_error(monkeypatch):
    """Test that polling continues after transient get() errors."""
    mock_client = MagicMock()
    initial = MockInteraction("test_123", "in_progress")
    mock_client.interactions.create.return_value = initial

    mock_client.interactions.get.side_effect = [
        Exception("Transient error"),
        MockInteraction("test_123", "completed", [MockTextOutput("Done")]),
    ]

    agent = DeepResearchAgent()
    agent.client = mock_client
    monkeypatch.setattr("time.sleep", MagicMock())
    agent.console = MagicMock()

    agent.research_poll("test prompt")
    assert mock_client.interactions.get.call_count == 2
```

### 2.7 Add CLI integration tests (optional)
**Location:** `tests/test_main.py`

Low priority - could add tests for:
- `--model` without `--previous-interaction-id` errors
- Multiple `--file-search` arguments
- `--no-stream` routes to `research_poll()`

### 2.8 Validate output_path at start of research_poll()
**Location:** `agent.py` (start of research_poll)

**Fix:** Match `research()` behavior by validating output path early.

```python
# At start of research_poll(), before API call:
if output_path:
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            pass  # Just test we can write
    except OSError as e:
        raise RuntimeError(f"Cannot write to '{output_path}': {e}") from e
```

---

## Implementation Order

1. **Important fixes** (1.1-1.4) - Raise exceptions instead of silent returns
2. **Critical test gaps** (1.5-1.7) - API key, max retries, timeout tests
3. **Docstring updates** (2.1-2.4) - Better documentation
4. **Additional tests** (2.5-2.6) - Edge case coverage
5. **Early validation** (2.8) - output_path check
6. **Run tests and lint** - Verify all changes

---

## Verification Checklist

- [ ] All 7 important issues addressed
- [ ] All 8 suggestions implemented
- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format .` passes
- [ ] `uv run pytest -v` passes (all existing + new tests)
