"""Tests for reliqua.middleware module."""

from unittest.mock import MagicMock

import falcon
import pytest

from reliqua.middleware import Converter, Parameter, ProcessParams, python_type, to_bool


class TestToBool:
    """Tests for the to_bool helper."""

    def test_truthy_strings(self):
        assert to_bool("true") is True
        assert to_bool("yes") is True
        assert to_bool("1") is True
        assert to_bool("on") is True
        assert to_bool("t") is True
        assert to_bool("y") is True

    def test_falsy_strings(self):
        assert to_bool("false") is False
        assert to_bool("no") is False
        assert to_bool("0") is False
        assert to_bool("off") is False
        assert to_bool("f") is False
        assert to_bool("n") is False
        assert to_bool("") is False

    def test_case_insensitive(self):
        assert to_bool("TRUE") is True
        assert to_bool("False") is False
        assert to_bool("YES") is True

    def test_whitespace_handling(self):
        assert to_bool("  true  ") is True
        assert to_bool("  false  ") is False

    def test_non_string_truthy(self):
        assert to_bool(1) is True
        assert to_bool([1]) is True

    def test_non_string_falsy(self):
        assert to_bool(0) is False


class TestPythonType:
    """Tests for the python_type helper."""

    def test_returns_builtin_types(self):
        assert python_type("str") is str
        assert python_type("int") is int
        assert python_type("float") is float
        assert python_type("list") is list
        assert python_type("dict") is dict
        assert python_type("bool") is bool

    def test_returns_none_for_unknown(self):
        assert python_type("nonexistent_type") is None

    def test_returns_none_for_empty_string(self):
        assert python_type("") is None


class TestParameter:
    """Tests for the Parameter class."""

    def test_default_attributes(self):
        p = Parameter()
        assert p.default is None
        assert p.required is False

    def test_kwargs_update(self):
        p = Parameter(name="test", datatype="str", required=True, default="hello")
        assert p.name == "test"
        assert p.datatype == "str"
        assert p.required is True
        assert p.default == "hello"


class TestConverter:
    """Tests for the Converter class."""

    def _make_request(self, params=None):
        """Create a mock Falcon request with params."""
        req = MagicMock(spec=falcon.Request)
        req.params = params or {}
        req.get_param = MagicMock(side_effect=lambda name, **kw: req.params.get(name, kw.get("default")))
        req.get_param_as_int = MagicMock(
            side_effect=lambda name, **kw: int(req.params[name]) if name in req.params else kw.get("default")
        )
        req.get_param_as_float = MagicMock(
            side_effect=lambda name, **kw: float(req.params[name]) if name in req.params else kw.get("default")
        )
        req.get_param_as_bool = MagicMock(
            side_effect=lambda name, **kw: bool(req.params[name]) if name in req.params else kw.get("default")
        )
        return req

    def test_as_str(self):
        req = self._make_request({"name": "alice"})
        result = Converter.as_str(req, "name")
        assert result == "alice"

    def test_as_int(self):
        req = self._make_request({"count": "42"})
        result = Converter.as_int(req, "count")
        assert result == 42

    def test_as_float(self):
        req = self._make_request({"rate": "3.14"})
        result = Converter.as_float(req, "rate")
        assert result == pytest.approx(3.14)

    def test_as_bool(self):
        req = self._make_request({"active": True})
        result = Converter.as_bool(req, "active")
        assert result is True

    def test_as_int_default(self):
        req = self._make_request({})
        result = Converter.as_int(req, "missing", default=10)
        assert result == 10

    def test_as_list_splits_csv_string(self):
        req = self._make_request({"items": "a, b, c"})
        req.get_param_as_list = MagicMock(return_value=["a", "b", "c"])
        result = Converter.as_list(req, "items")
        assert result == ["a", "b", "c"]

    def test_as_list_filters_empty_strings(self):
        req = self._make_request({"items": ["a", "", "c"]})
        req.get_param_as_list = MagicMock(return_value=["a", "", "c"])
        result = Converter.as_list(req, "items")
        assert result == ["a", "c"]

    def test_as_array_returns_value(self):
        """as_array should return the result (not None)."""
        req = self._make_request({"items": ["a", "b"]})
        req.get_param_as_list = MagicMock(return_value=["a", "b"])
        result = Converter.as_array(req, "items")
        assert result == ["a", "b"]


class TestProcessParams:
    """Tests for the ProcessParams middleware."""

    def test_check_required_raises_on_missing(self):
        pp = ProcessParams()
        req = MagicMock()
        req.params = {}
        param = Parameter(name="username", required=True, default=None)
        with pytest.raises(falcon.HTTPBadRequest):
            pp._check_required(req, param)

    def test_check_required_passes_with_value(self):
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"username": "alice"}
        param = Parameter(name="username", required=True, default=None)
        pp._check_required(req, param)  # should not raise

    def test_check_required_passes_with_default(self):
        pp = ProcessParams()
        req = MagicMock()
        req.params = {}
        param = Parameter(name="username", required=True, default="guest")
        pp._check_required(req, param)  # should not raise

    def test_check_required_passes_with_empty_string(self):
        """An empty string is a valid provided value, should not raise."""
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"tags": ""}
        param = Parameter(name="tags", required=True, default=None)
        pp._check_required(req, param)  # should not raise

    def test_check_required_passes_with_empty_list(self):
        """An empty list is a valid provided value, should not raise."""
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"items": []}
        param = Parameter(name="items", required=True, default=None)
        pp._check_required(req, param)  # should not raise

    def test_check_required_passes_with_empty_dict(self):
        """An empty dict is a valid provided value, should not raise."""
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"config": {}}
        param = Parameter(name="config", required=True, default=None)
        pp._check_required(req, param)  # should not raise

    def test_check_required_passes_with_zero(self):
        """Zero is a valid provided value, should not raise."""
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"count": 0}
        param = Parameter(name="count", required=True, default=None)
        pp._check_required(req, param)  # should not raise

    def test_check_required_passes_with_false(self):
        """False is a valid provided value, should not raise."""
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"active": False}
        param = Parameter(name="active", required=True, default=None)
        pp._check_required(req, param)  # should not raise

    def test_parse_operators(self):
        pp = ProcessParams()
        req = MagicMock()
        req.params = {"name__in": ["a", "b"], "age__between": [10, 20]}
        operators = pp._parse_operators(req)
        assert operators["name"] == "in"
        assert operators["age"] == "between"
        assert "name" in req.params
        assert "age" in req.params

    def test_get_resource_parameters_returns_empty_on_missing(self):
        req = MagicMock()
        req.uri_template = "/missing"
        req.method = "GET"
        resource = MagicMock()
        resource.__data__ = {}
        result = ProcessParams.get_resource_parameters(req, resource)
        assert result == []

    def test_get_resource_parameters_returns_parameters(self):
        req = MagicMock()
        req.uri_template = "/users"
        req.method = "get"
        resource = MagicMock()
        resource.__data__ = {
            "/users": {
                "get": {
                    "parameters": [
                        {"name": "username", "datatype": "str", "required": False},
                    ]
                }
            }
        }
        result = ProcessParams.get_resource_parameters(req, resource)
        assert len(result) == 1
        assert result[0].name == "username"
