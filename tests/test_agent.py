import os
import sys
from unittest.mock import MagicMock

import pytest

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from radiant_filament.agent import DeepResearchAgent


class MockEvent:
    def __init__(self, event_type, event_id=None, text=None, restart=False):
        self.event_type = event_type
        self.event_id = event_id
        self.delta = MagicMock()
        if text:
            self.delta.type = "text"
            self.delta.text = text
        else:
            self.delta.type = "other"

        self.interaction = MagicMock()
        if restart:
            self.interaction.id = "new_interaction_id"


def test_agent_initialization():
    agent = DeepResearchAgent()
    assert agent.agent_name == "deep-research-pro-preview-12-2025"


def test_robust_stream_recovers_from_error(monkeypatch):
    """
    Simulates a stream that fails after the first item, then succeeds on reconnection.
    """
    mock_client = MagicMock()

    # Stream 1: Yields one event then raises Exception
    def stream_1():
        yield MockEvent("interaction.start", restart=True)
        yield MockEvent("content.delta", event_id="1", text="Hello")
        raise Exception("Connection dropped")

    # Stream 2: Resumes, yields more events, completes
    def stream_2():
        yield MockEvent("content.delta", event_id="2", text=" World")
        yield MockEvent("interaction.complete")

    # Mock the interactions.create and get methods
    mock_client.interactions.create.return_value = stream_1()
    mock_client.interactions.get.return_value = stream_2()

    # Init agent with mock client
    agent = DeepResearchAgent()
    agent.client = mock_client

    # We need to mock time.sleep to speed up test
    mock_sleep = MagicMock()
    monkeypatch.setattr("time.sleep", mock_sleep)

    # We will use the internal _robust_stream generator (which we plan to implement)
    # If the implementation name changes, this test will need update.
    # For now assuming we implement `robust_research_stream(prompt)` or similar.
    # Or we can test `research` but we need to mock the UI to avoiding printing.

    # Let's assume we extract the generator to `agent.interact(prompt)` returning a generator.

    # Since I haven't implemented it yet, I will verify the logic by calling the new method I plan to add:
    # `events = agent.start_research_stream("test prompt")`

    # But wait, `research` is the main entry. I'll modify `research` to use `start_research_stream`.
    # Let's test `start_research_stream`.

    events = list(agent.start_research_stream("test prompt"))

    # Verification
    # 1. Check all events are received
    assert len(events) == 4  # start, Hello, World, complete
    assert events[1].delta.text == "Hello"
    assert events[2].delta.text == " World"

    # 2. Check reconnection happened
    # interactions.create called once
    mock_client.interactions.create.assert_called_once()
    # interactions.get called once with correct ID
    mock_client.interactions.get.assert_called_once()
    _, kwargs = mock_client.interactions.get.call_args
    assert kwargs["id"] == "new_interaction_id"
    assert kwargs["last_event_id"] == "1"


def test_initial_connection_failure_raises():
    """
    Ensures that if the initial connection fails (before interaction_id is set),
    the exception is raised instead of being swallowed.
    """
    mock_client = MagicMock()
    mock_client.interactions.create.side_effect = Exception("API Error")

    agent = DeepResearchAgent()
    agent.client = mock_client

    with pytest.raises(Exception, match="API Error"):
        list(agent.start_research_stream("test prompt"))


def test_merge_agent_config_with_none():
    """Test that None config returns defaults."""
    agent = DeepResearchAgent()
    result = agent._merge_agent_config(None)
    assert result == {"type": "deep-research", "thinking_summaries": "auto"}


def test_merge_agent_config_with_override():
    """Test that user config overrides defaults."""
    agent = DeepResearchAgent()
    result = agent._merge_agent_config({"thinking_summaries": "none"})
    assert result == {"type": "deep-research", "thinking_summaries": "none"}


def test_merge_agent_config_preserves_type():
    """Test that type is preserved unless explicitly overridden."""
    agent = DeepResearchAgent()
    result = agent._merge_agent_config({"custom_key": "value"})
    assert result["type"] == "deep-research"
    assert result["custom_key"] == "value"


def test_stream_with_previous_interaction_id(monkeypatch):
    """Test that previous_interaction_id is passed to create."""
    mock_client = MagicMock()

    def stream():
        yield MockEvent("interaction.start", restart=True)
        yield MockEvent("interaction.complete")

    mock_client.interactions.create.return_value = stream()

    agent = DeepResearchAgent()
    agent.client = mock_client

    list(agent.start_research_stream("follow-up", previous_interaction_id="prev_123"))

    _, kwargs = mock_client.interactions.create.call_args
    assert kwargs["previous_interaction_id"] == "prev_123"


def test_stream_with_model_instead_of_agent(monkeypatch):
    """Test that model parameter replaces agent parameter."""
    mock_client = MagicMock()

    def stream():
        yield MockEvent("interaction.start", restart=True)
        yield MockEvent("interaction.complete")

    mock_client.interactions.create.return_value = stream()

    agent = DeepResearchAgent()
    agent.client = mock_client

    list(
        agent.start_research_stream(
            "summarize", previous_interaction_id="prev_123", model="gemini-2.5-pro"
        )
    )

    _, kwargs = mock_client.interactions.create.call_args
    assert kwargs["model"] == "gemini-2.5-pro"
    assert "agent" not in kwargs
    assert "agent_config" not in kwargs


def test_stream_with_tools(monkeypatch):
    """Test that tools are passed to create."""
    mock_client = MagicMock()

    def stream():
        yield MockEvent("interaction.start", restart=True)
        yield MockEvent("interaction.complete")

    mock_client.interactions.create.return_value = stream()

    agent = DeepResearchAgent()
    agent.client = mock_client

    tools = [
        {
            "type": "file_search",
            "file_search_store_names": ["fileSearchStores/my-store"],
        }
    ]
    list(agent.start_research_stream("analyze docs", tools=tools))

    _, kwargs = mock_client.interactions.create.call_args
    assert kwargs["tools"] == tools


class MockTextOutput:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class MockInteraction:
    def __init__(self, interaction_id, status, outputs=None):
        self.id = interaction_id
        self.status = status
        self.outputs = outputs or []


def test_poll_creates_interaction_without_stream(monkeypatch):
    """Test that research_poll creates interaction with stream=False."""
    mock_client = MagicMock()
    mock_interaction = MockInteraction(
        "test_123", "completed", [MockTextOutput("Done")]
    )
    mock_client.interactions.create.return_value = mock_interaction
    mock_client.interactions.get.return_value = mock_interaction

    agent = DeepResearchAgent()
    agent.client = mock_client

    # Mock sleep and console to speed up test
    monkeypatch.setattr("time.sleep", MagicMock())
    agent.console = MagicMock()

    agent.research_poll("test prompt")

    _, kwargs = mock_client.interactions.create.call_args
    assert kwargs["stream"] is False
    assert kwargs["background"] is True


def test_poll_polls_until_completed(monkeypatch):
    """Test that research_poll polls until status is completed."""
    mock_client = MagicMock()

    # Initial response: in_progress
    initial_interaction = MockInteraction("test_123", "in_progress")
    mock_client.interactions.create.return_value = initial_interaction

    # Subsequent get calls: in_progress, then completed
    poll_1 = MockInteraction("test_123", "in_progress")
    poll_2 = MockInteraction("test_123", "completed", [MockTextOutput("Final report")])
    mock_client.interactions.get.side_effect = [poll_1, poll_2]

    agent = DeepResearchAgent()
    agent.client = mock_client

    # Mock sleep and console
    mock_sleep = MagicMock()
    monkeypatch.setattr("time.sleep", mock_sleep)
    agent.console = MagicMock()

    agent.research_poll("test prompt", poll_interval=1)

    # Should have called get twice
    assert mock_client.interactions.get.call_count == 2
    # Should have slept twice
    assert mock_sleep.call_count == 2


def test_poll_handles_failed_status(monkeypatch):
    """Test that research_poll raises RuntimeError on failed status."""
    mock_client = MagicMock()
    mock_interaction = MockInteraction("test_123", "failed")
    mock_client.interactions.create.return_value = mock_interaction

    agent = DeepResearchAgent()
    agent.client = mock_client

    monkeypatch.setattr("time.sleep", MagicMock())
    agent.console = MagicMock()

    with pytest.raises(RuntimeError, match="Research failed"):
        agent.research_poll("test prompt")

    # Should also print error message
    agent.console.print.assert_called()


def test_poll_extracts_text_from_outputs(monkeypatch):
    """Test that research_poll extracts text from outputs correctly."""
    mock_client = MagicMock()
    outputs = [MockTextOutput("Part 1"), MockTextOutput("Part 2")]
    mock_interaction = MockInteraction("test_123", "completed", outputs)
    mock_client.interactions.create.return_value = mock_interaction

    agent = DeepResearchAgent()
    agent.client = mock_client

    monkeypatch.setattr("time.sleep", MagicMock())
    agent.console = MagicMock()

    agent.research_poll("test prompt")

    # Console.print should have been called with Markdown containing concatenated text
    from rich.markdown import Markdown

    calls = agent.console.print.call_args_list
    markdown_calls = [c for c in calls if isinstance(c[0][0], Markdown)]
    assert len(markdown_calls) > 0


def test_poll_handles_create_exception(monkeypatch):
    """Test that research_poll handles create() exceptions."""
    mock_client = MagicMock()
    mock_client.interactions.create.side_effect = Exception("API unavailable")

    agent = DeepResearchAgent()
    agent.client = mock_client
    agent.console = MagicMock()

    with pytest.raises(Exception, match="API unavailable"):
        agent.research_poll("test prompt")

    # Should have printed error message before raising
    agent.console.print.assert_called()


def test_poll_handles_cancelled_status(monkeypatch):
    """Test that research_poll raises RuntimeError on cancelled status."""
    mock_client = MagicMock()
    mock_interaction = MockInteraction("test_123", "cancelled")
    mock_client.interactions.create.return_value = mock_interaction

    agent = DeepResearchAgent()
    agent.client = mock_client

    monkeypatch.setattr("time.sleep", MagicMock())
    agent.console = MagicMock()

    with pytest.raises(RuntimeError, match="cancelled"):
        agent.research_poll("test prompt")

    # Should also print cancelled message
    agent.console.print.assert_called()


def test_poll_saves_to_output_path(monkeypatch, tmp_path):
    """Test that research_poll saves output to file when path provided."""
    mock_client = MagicMock()
    mock_interaction = MockInteraction(
        "test_123", "completed", [MockTextOutput("Report content")]
    )
    mock_client.interactions.create.return_value = mock_interaction

    agent = DeepResearchAgent()
    agent.client = mock_client

    monkeypatch.setattr("time.sleep", MagicMock())
    agent.console = MagicMock()

    output_file = tmp_path / "output.md"
    agent.research_poll("test prompt", output_path=str(output_file))

    assert output_file.exists()
    assert output_file.read_text() == "Report content"
