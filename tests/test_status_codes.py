"""Tests for reliqua.status_codes module."""

from reliqua.status_codes import CODES, MESSAGES, http


class TestHttp:
    """Tests for the http() function."""

    def test_http_with_numeric_code(self):
        """Return formatted status string for a numeric code."""
        assert http(200) == "200 OK"

    def test_http_with_string_code(self):
        """Return formatted status string for a string code."""
        assert http("404") == "404 Not Found"

    def test_http_common_codes(self):
        """Verify common HTTP status codes."""
        assert http(201) == "201 Created"
        assert http(400) == "400 Bad Request"
        assert http(401) == "401 Unauthorized"
        assert http(403) == "403 Forbidden"
        assert http(500) == "500 Internal Server Error"

    def test_http_with_message_key(self):
        """Return status string when given a message name."""
        assert http("NOT_FOUND") == "404 NOT_FOUND"
        assert http("OK") == "200 OK"
        assert http("BAD_REQUEST") == "400 BAD_REQUEST"


class TestMessages:
    """Tests for the MESSAGES dict."""

    def test_messages_is_dict(self):
        """MESSAGES should be a dict, not a set."""
        assert isinstance(MESSAGES, dict)

    def test_messages_lookup(self):
        """MESSAGES keys should map to status code strings."""
        assert MESSAGES["OK"] == "200"
        assert MESSAGES["NOT_FOUND"] == "404"
        assert MESSAGES["BAD_REQUEST"] == "400"
        assert MESSAGES["INTERNAL_SERVER_ERROR"] == "500"

    def test_messages_has_all_codes(self):
        """MESSAGES should have an entry for every code."""
        assert len(MESSAGES) == len(CODES)


class TestCodes:
    """Tests for the CODES dict."""

    def test_codes_is_dict(self):
        """CODES should be a dict."""
        assert isinstance(CODES, dict)

    def test_codes_has_common_entries(self):
        """CODES should contain common HTTP status codes."""
        assert CODES["200"] == "OK"
        assert CODES["404"] == "Not Found"
        assert CODES["500"] == "Internal Server Error"
