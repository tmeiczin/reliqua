"""Tests for reliqua.media_handlers module."""

import io
import json
from datetime import date, datetime, time

from reliqua.media_handlers import JSONHandler, TextHandler, YAMLHandler


class TestJSONHandler:
    """Tests for the JSONHandler."""

    def test_serialize_basic(self):
        handler = JSONHandler()
        data = {"name": "alice", "age": 30}
        result = handler.serialize(data, "application/json")
        parsed = json.loads(result)
        assert parsed == data

    def test_serialize_datetime(self):
        handler = JSONHandler()
        dt = datetime(2024, 1, 15, 10, 30, 0)
        data = {"created": dt}
        result = handler.serialize(data, "application/json")
        parsed = json.loads(result)
        assert parsed["created"] == str(dt)

    def test_serialize_date(self):
        handler = JSONHandler()
        d = date(2024, 1, 15)
        data = {"date": d}
        result = handler.serialize(data, "application/json")
        parsed = json.loads(result)
        assert parsed["date"] == str(d)

    def test_serialize_time(self):
        handler = JSONHandler()
        t = time(10, 30, 0)
        data = {"time": t}
        result = handler.serialize(data, "application/json")
        parsed = json.loads(result)
        assert parsed["time"] == str(t)

    def test_serialize_unicode(self):
        handler = JSONHandler()
        data = {"name": "héllo wörld"}
        result = handler.serialize(data, "application/json")
        # ensure_ascii=False means unicode chars are preserved
        assert "héllo" in result.decode("utf-8") if isinstance(result, bytes) else "héllo" in result


class TestTextHandler:
    """Tests for the TextHandler."""

    def test_serialize_string(self):
        handler = TextHandler()
        result = handler.serialize("hello world", "text/plain")
        assert result == b"hello world"

    def test_serialize_number(self):
        handler = TextHandler()
        result = handler.serialize(42, "text/plain")
        assert result == b"42"

    def test_deserialize(self):
        handler = TextHandler()
        stream = io.BytesIO(b"hello world")
        result = handler.deserialize(stream, "text/plain", len(b"hello world"))
        assert result == "hello world"


class TestYAMLHandler:
    """Tests for the YAMLHandler."""

    def test_serialize(self):
        handler = YAMLHandler()
        data = {"name": "alice", "age": 30}
        result = handler.serialize(data, "application/yaml")
        assert b"name: alice" in result

    def test_deserialize(self):
        handler = YAMLHandler()
        yaml_content = b"name: alice\nage: 30\n"
        stream = io.BytesIO(yaml_content)
        result = handler.deserialize(stream, "application/yaml", len(yaml_content))
        assert result["name"] == "alice"
        assert result["age"] == 30
