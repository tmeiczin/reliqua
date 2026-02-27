"""Tests for reliqua.database module."""

from base64 import b64encode

from reliqua.database import is_b64


class TestIsB64:
    """Tests for the is_b64 helper."""

    def test_valid_base64_string(self):
        """A valid base64 str should return True."""
        encoded = b64encode(b"hello world").decode("utf-8")
        assert is_b64(encoded) is True

    def test_valid_base64_bytes(self):
        """A valid base64 bytes should return True."""
        encoded = b64encode(b"hello world")
        assert is_b64(encoded) is True

    def test_invalid_base64_string(self):
        """A non-base64 string should return False."""
        assert is_b64("not-base64!!!") is False

    def test_empty_string(self):
        """An empty string is valid base64."""
        assert is_b64("") is True

    def test_none_returns_false(self):
        """None should return False."""
        assert is_b64(None) is False

    def test_plain_text_not_base64(self):
        """Arbitrary plain text that isn't valid base64 returns False."""
        assert is_b64("hello world") is False

    def test_password_roundtrip(self):
        """A base64-encoded password should be detectable."""
        password = "s3cr3t_p@ssw0rd"
        encoded = b64encode(password.encode("utf-8")).decode("utf-8")
        assert is_b64(encoded) is True
