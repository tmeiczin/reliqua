"""Tests for reliqua.openapi module."""

from reliqua.openapi import (
    BINARY_TYPES,
    CONTENT_MAP,
    TYPE_MAP,
    Contact,
    License,
    Operation,
    Parameter,
    Response,
    camelcase,
)


class TestCamelcase:
    """Tests for the camelcase helper."""

    def test_single_word(self):
        assert camelcase("hello") == "hello"

    def test_two_words(self):
        assert camelcase("hello_world") == "helloWorld"

    def test_three_words(self):
        assert camelcase("one_two_three") == "oneTwoThree"

    def test_empty_string(self):
        assert camelcase("") == ""


class TestParameter:
    """Tests for the OpenAPI Parameter class."""

    def test_basic_string_parameter(self):
        p = Parameter(name="username", datatype="str", location="query")
        assert p.datatype == "string"
        assert p.name == "username"
        assert p.location == "query"

    def test_path_parameter_always_required(self):
        p = Parameter(name="id", datatype="int", location="path", required=False)
        assert p.required is True

    def test_list_datatype(self):
        p = Parameter(name="ids", datatype="list[int]")
        assert p.datatype == "array"
        assert p.items_type == "integer"

    def test_pipe_separated_type(self):
        p = Parameter(name="value", datatype="str|int")
        assert p.datatype == "string|integer"

    def test_no_items_type_for_non_list(self):
        p = Parameter(name="name", datatype="str")
        assert p.items_type is None

    def test_schema_includes_enum(self):
        p = Parameter(name="status", datatype="str", enum=["active", "inactive"])
        assert p.schema["enum"] == ["active", "inactive"]

    def test_schema_includes_default(self):
        p = Parameter(name="page", datatype="int", default=1)
        assert p.schema["default"] == 1

    def test_in_request_body_for_body_location(self):
        p = Parameter(name="data", datatype="str", location="body")
        assert p.in_request_body() is True

    def test_in_request_body_for_form_location(self):
        p = Parameter(name="data", datatype="str", location="form")
        assert p.in_request_body() is True

    def test_not_in_request_body_for_query(self):
        p = Parameter(name="data", datatype="str", location="query")
        assert p.in_request_body() is False

    def test_parameter_dict_for_query(self):
        p = Parameter(name="q", datatype="str", location="query", description="Search")
        d = p.dict()
        assert d["name"] == "q"
        assert d["in"] == "query"

    def test_parameter_dict_for_body(self):
        p = Parameter(name="data", datatype="str", location="body", description="Body data")
        d = p.dict()
        # body parameters return the request_body schema
        assert "type" in d


class TestResponse:
    """Tests for the Response class."""

    def test_basic_response(self):
        r = Response(code="200", description="Success", content=["json"])
        d = r.dict()
        assert d["description"] == "Success"
        assert "application/json" in d["content"]

    def test_default_schema(self):
        r = Response(code="200", description="OK", content=["json"])
        assert r.schema == "default_response"

    def test_custom_schema(self):
        r = Response(code="200", description="OK", content=["json"], schema="user")
        assert r.schema == "user"

    def test_multiple_content_types(self):
        r = Response(code="200", description="OK", content=["json", "xml"])
        d = r.dict()
        assert "application/json" in d["content"]
        assert "application/xml" in d["content"]


class TestOperation:
    """Tests for the Operation class."""

    def test_basic_operation(self):
        op = Operation(
            operation="get",
            summary="Get users",
            description="Returns all users",
            operation_id="getUsers",
            parameters=[],
            responses=[{"code": "200", "description": "OK"}],
            return_types=["json"],
        )
        d = op.dict()
        assert "get" in d
        assert d["get"]["summary"] == "Get users"
        assert d["get"]["operationId"] == "getUsers"

    def test_operation_with_parameters(self):
        op = Operation(
            operation="get",
            summary="Test",
            description="Test",
            operation_id="test",
            parameters=[{"name": "id", "datatype": "int", "location": "path"}],
            responses=[],
            return_types=["json"],
        )
        d = op.dict()
        assert len(d["get"]["parameters"]) == 1
        assert d["get"]["parameters"][0]["name"] == "id"

    def test_operation_with_body_parameters(self):
        op = Operation(
            operation="post",
            summary="Create",
            description="Create item",
            operation_id="createItem",
            parameters=[
                {"name": "data", "datatype": "str", "location": "body", "description": "Data", "required": True}
            ],
            responses=[],
            return_types=["json"],
        )
        d = op.dict()
        # body params should not appear in parameters list
        assert len(d["post"]["parameters"]) == 0
        assert "requestBody" in d["post"]

    def test_request_body_binary_type(self):
        """Binary accept types should produce binary body schema."""
        op = Operation(
            operation="post",
            summary="Upload",
            description="Upload file",
            operation_id="upload",
            parameters=[{"name": "file", "datatype": "str", "location": "body", "description": "File"}],
            responses=[],
            return_types=["binary"],
            accepts=["binary"],
        )
        body = op.request_body()
        assert "content" in body
        assert "application/octet-stream" in body["content"]

    def test_request_body_json_type(self):
        """JSON accept types should produce normal body schema."""
        op = Operation(
            operation="post",
            summary="Create",
            description="Create",
            operation_id="create",
            parameters=[{"name": "data", "datatype": "str", "location": "body", "description": "Data"}],
            responses=[],
            return_types=["json"],
            accepts=["json"],
        )
        body = op.request_body()
        assert "content" in body
        assert "application/json" in body["content"]

    def test_has_form(self):
        op = Operation(
            operation="post",
            summary="Form",
            description="Form",
            operation_id="form",
            parameters=[{"name": "field", "datatype": "str", "location": "form", "description": "Field"}],
            responses=[],
            return_types=["json"],
        )
        assert op.has_form() is True

    def test_no_form(self):
        op = Operation(
            operation="get",
            summary="Get",
            description="Get",
            operation_id="get",
            parameters=[{"name": "q", "datatype": "str", "location": "query"}],
            responses=[],
            return_types=["json"],
        )
        assert op.has_form() is False


class TestContact:
    """Tests for the Contact class."""

    def test_contact_dict(self):
        c = Contact(name="Alice", url="https://example.com", email="alice@example.com")
        d = c.dict()
        assert d["name"] == "Alice"
        assert d["url"] == "https://example.com"
        assert d["email"] == "alice@example.com"

    def test_contact_repr(self):
        c = Contact(name="Alice")
        assert "Alice" in repr(c)


class TestLicense:
    """Tests for the License class."""

    def test_license_dict(self):
        lic = License(name="MIT", url="https://mit.edu")
        d = lic.dict()
        assert d["name"] == "MIT"
        assert d["url"] == "https://mit.edu"

    def test_license_defaults(self):
        lic = License()
        assert lic.name == ""
        assert lic.url == ""


class TestContentMap:
    """Tests for module-level constants."""

    def test_json_mapping(self):
        assert CONTENT_MAP["json"] == "application/json"

    def test_binary_mapping(self):
        assert CONTENT_MAP["binary"] == "application/octet-stream"

    def test_binary_types_list(self):
        assert "binary" in BINARY_TYPES
        assert "gzip" in BINARY_TYPES

    def test_type_map(self):
        assert TYPE_MAP["str"] == "string"
        assert TYPE_MAP["int"] == "integer"
        assert TYPE_MAP["list"] == "array"
        assert TYPE_MAP["dict"] == "object"
