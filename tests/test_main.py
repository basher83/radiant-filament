import json
import os
import sys
import tempfile

import pytest

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from radiant_filament.main import parse_agent_config, validate_file_search_store


class TestParseAgentConfig:
    def test_none_returns_none(self):
        assert parse_agent_config(None) is None

    def test_valid_json_string(self):
        result = parse_agent_config('{"thinking_summaries": "none"}')
        assert result == {"thinking_summaries": "none"}

    def test_invalid_json_raises(self):
        import argparse

        with pytest.raises(argparse.ArgumentTypeError, match="Invalid JSON"):
            parse_agent_config("not valid json")

    def test_json_file_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"type": "custom", "key": "value"}, f)
            f.flush()

            try:
                result = parse_agent_config(f.name)
                assert result == {"type": "custom", "key": "value"}
            finally:
                os.unlink(f.name)


class TestValidateFileSearchStore:
    def test_valid_store_name(self):
        result = validate_file_search_store("fileSearchStores/my-store")
        assert result == "fileSearchStores/my-store"

    def test_invalid_store_name_raises(self):
        import argparse

        with pytest.raises(argparse.ArgumentTypeError, match="Invalid store format"):
            validate_file_search_store("invalid-store-name")

    def test_partial_match_raises(self):
        import argparse

        with pytest.raises(argparse.ArgumentTypeError):
            validate_file_search_store("fileSearchStores")
