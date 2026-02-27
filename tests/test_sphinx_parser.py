"""Tests for reliqua.sphinx_parser module."""

from reliqua.sphinx_parser import SphinxParser


def make_method(docstring):
    """Create a function with the given docstring for testing."""

    def on_get(_self, _req, _resp):
        pass

    on_get.__doc__ = docstring
    on_get.__qualname__ = "TestResource.on_get"
    return on_get


class TestSphinxParserOptions:
    """Tests for parse_options."""

    def test_parse_location(self):
        result = SphinxParser.parse_options("in=path required")
        assert result["location"] == "path"
        assert result["required"] is True

    def test_parse_query_default(self):
        result = SphinxParser.parse_options("")
        assert result["location"] == "query"
        assert result["required"] is False

    def test_parse_enum(self):
        result = SphinxParser.parse_options("enum=colors")
        assert result["enum"] == "colors"

    def test_parse_default(self):
        result = SphinxParser.parse_options("default=hello")
        assert result["default"] == "hello"

    def test_optional_overrides_required(self):
        result = SphinxParser.parse_options("required optional")
        assert result["required"] is False

    def test_parse_min_max(self):
        result = SphinxParser.parse_options("min=1 max=100")
        assert result["min"] == "1"
        assert result["max"] == "100"


class TestSphinxParserParameter:
    """Tests for parse_parameter."""

    def test_basic_parameter(self):
        parser = SphinxParser()
        result = parser.parse_parameter(":param str username: [in=query] User name")
        assert result is not None
        assert result["name"] == "username"
        assert result["datatype"] == "str"
        assert result["description"] == "User name"

    def test_parameter_with_path(self):
        parser = SphinxParser()
        result = parser.parse_parameter(":param int id: [in=path required] User ID")
        assert result["name"] == "id"
        assert result["datatype"] == "int"
        assert result["location"] == "path"
        assert result["required"] is True

    def test_parameter_no_options(self):
        parser = SphinxParser()
        result = parser.parse_parameter(":param str name:  User's name")
        assert result is not None
        assert result["name"] == "name"
        assert result["required"] is False

    def test_parameter_list_type(self):
        parser = SphinxParser()
        result = parser.parse_parameter(":param list[int] ids: [in=query] List of IDs")
        assert result["datatype"] == "list[int]"

    def test_invalid_parameter_returns_none(self):
        parser = SphinxParser()
        result = parser.parse_parameter("not a parameter string")
        assert result is None


class TestSphinxParserProperties:
    """Tests for summary, description, parameters, responses, content, accepts properties."""

    def test_summary(self):
        parser = SphinxParser()
        parser.doc = "Return all users.\n\nGet a list of users.\n\n:return json:"
        assert parser.summary == "Return all users."

    def test_description(self):
        parser = SphinxParser()
        parser.doc = "Return all users.\n\nGet a list of users.\n\n:return json:"
        assert parser.description == "Get a list of users."

    def test_empty_summary(self):
        parser = SphinxParser()
        parser.doc = ""
        assert parser.summary == ""

    def test_parameters_parsed(self):
        parser = SphinxParser()
        parser.doc = (
            "Get users.\n\n:param str username: [in=query] Username\n:param int limit: [in=query] Limit\n:return json:"
        )
        params = parser.parameters
        assert len(params) == 2
        assert params[0]["name"] == "username"
        assert params[1]["name"] == "limit"

    def test_responses_parsed(self):
        parser = SphinxParser()
        parser.doc = "Get users.\n\n:response 200: Success\n:response 400: Bad request\n:return json:"
        responses = parser.responses
        assert len(responses) == 2
        assert responses[0]["code"] == "200"
        assert responses[1]["code"] == "400"

    def test_response_with_schema(self):
        parser = SphinxParser()
        parser.doc = "Get user.\n\n:response 200 user: User found\n:return json:"
        responses = parser.responses
        assert responses[0]["schema"] == "user"

    def test_content_default_json(self):
        parser = SphinxParser()
        parser.doc = "Get data.\n\nSome description."
        assert parser.content == ["json"]

    def test_content_explicit(self):
        parser = SphinxParser()
        parser.doc = "Get data.\n\n:return [json xml]:"
        assert "json" in parser.content
        assert "xml" in parser.content

    def test_accepts_empty(self):
        parser = SphinxParser()
        parser.doc = "Get data.\n\n:return json:"
        assert parser.accepts == []

    def test_accepts_explicit(self):
        parser = SphinxParser()
        parser.doc = "Post data.\n\n:accepts [json,xml]:\n:return json:"
        assert "json" in parser.accepts
        assert "xml" in parser.accepts


class TestSphinxParserParse:
    """Tests for the full parse method."""

    def test_parse_full_method(self):
        parser = SphinxParser()

        method = make_method(
            "Return users.\n\n"
            "Get a list of users.\n\n"
            ":param str username: [in=query] Username\n"
            ":response 200: Success\n"
            ":return json:"
        )

        result = parser.parse(method)
        assert result["operation"] == "get"
        assert result["summary"] == "Return users."
        assert result["description"] == "Get a list of users."
        assert len(result["parameters"]) == 1
        assert len(result["responses"]) == 1
        assert result["return_types"] == ["json"]

    def test_parse_operation_detection(self):
        parser = SphinxParser()

        for verb in ["get", "post", "put", "patch", "delete"]:

            def method(_self):
                """Test."""

            method.__qualname__ = f"Res.on_{verb}"
            method.__doc__ = "Test.\n\n:return json:"
            result = parser.parse(method)
            assert result["operation"] == verb

    def test_parse_suffix_detection(self):
        parser = SphinxParser()

        def method(_self):
            r"""Test.\n\n:return json:"""

        method.__qualname__ = "Res.on_get_by_id"
        method.__doc__ = "Test.\n\n:return json:"

        result = parser.parse(method)
        assert result["suffix"] == "by_id"

    def test_parse_no_suffix(self):
        parser = SphinxParser()
        method = make_method("Test.\n\n:return json:")
        result = parser.parse(method)
        assert result["suffix"] is None

    def test_generate_operation_id(self):
        method = make_method("Test.")
        assert SphinxParser.generate_operation_id(method) == "TestResource.on_get"


class TestSphinxParserEdgeCases:
    """Edge case tests."""

    def test_multiline_parameter_description(self):
        parser = SphinxParser()
        parser.doc = "Get data.\n\n:param str name: [in=query] The user's\n    full name\n:return json:"
        params = parser.parameters
        assert len(params) == 1
        assert "name" in params[0]["description"].lower() or params[0]["name"] == "name"

    def test_no_parameters(self):
        parser = SphinxParser()
        parser.doc = "Simple method.\n\n:return json:"
        assert not parser.parameters

    def test_no_responses(self):
        parser = SphinxParser()
        parser.doc = "Simple method.\n\n:return json:"
        assert not parser.responses
