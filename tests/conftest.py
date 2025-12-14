import pytest


@pytest.fixture
def mock_genai_client(monkeypatch):
    """Mocks the google.genai.Client for testing."""

    class MockClient:
        def __init__(self, api_key=None):
            self.interactions = MockInteractions()

    class MockInteractions:
        def create(self, **kwargs):
            pass

        def get(self, **kwargs):
            pass

    # We will refine this structure in the actual test file or here as needed.
    # For now, just a placeholder if we need shared fixtures.
    pass
