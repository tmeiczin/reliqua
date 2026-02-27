"""Tests for reliqua.app utility functions."""

import os
import tempfile

from reliqua.app import load_config, update_dict


class TestUpdateDict:
    """Tests for the update_dict function."""

    def test_keeps_only_common_keys_from_a(self):
        a = {"x": 1, "y": 2, "z": 3}
        b = {"x": 10, "y": 20}
        result = update_dict(a, b)
        assert result == {"x": 1, "y": 2}

    def test_adds_keys_from_b_not_in_a(self):
        a = {"x": 1}
        b = {"x": 10, "y": 20, "z": 30}
        result = update_dict(a, b)
        assert result == {"x": 1, "y": 20, "z": 30}

    def test_empty_a(self):
        a = {}
        b = {"x": 1, "y": 2}
        result = update_dict(a, b)
        assert result == {"x": 1, "y": 2}

    def test_empty_b(self):
        a = {"x": 1, "y": 2}
        b = {}
        result = update_dict(a, b)
        assert result == {}

    def test_both_empty(self):
        result = update_dict({}, {})
        assert result == {}

    def test_no_overlap(self):
        a = {"x": 1}
        b = {"y": 2}
        result = update_dict(a, b)
        assert result == {"y": 2}

    def test_does_not_mutate_inputs(self):
        a = {"x": 1, "y": 2}
        b = {"x": 10}
        a_copy = a.copy()
        b_copy = b.copy()
        update_dict(a, b)
        assert a == a_copy
        assert b == b_copy


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_load_valid_config(self):
        config_content = "[config]\ntitle = My App\nversion = 2.0.0\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write(config_content)
            f.flush()
            result = load_config(f.name)
        os.unlink(f.name)
        assert result["title"] == "My App"
        assert result["version"] == "2.0.0"

    def test_load_nonexistent_file(self):
        result = load_config("/nonexistent/config.ini")
        assert not result

    def test_load_none(self):
        result = load_config(None)
        assert not result

    def test_load_empty_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("")
            f.flush()
            result = load_config(f.name)
        os.unlink(f.name)
        assert not result

    def test_load_config_missing_section(self):
        config_content = "[other]\nkey = value\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write(config_content)
            f.flush()
            result = load_config(f.name)
        os.unlink(f.name)
        assert result == {}
