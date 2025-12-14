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
