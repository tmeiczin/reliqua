"""Tests for reliqua.exceptions module (dynamic exception classes)."""

# pylint: disable=no-member

from falcon.http_error import HTTPError

import reliqua.exceptions as exc


class TestDynamicExceptionClasses:
    """Tests for dynamically generated HTTP exception classes."""

    def test_common_classes_exist(self):
        """Common exception classes should be importable."""
        assert hasattr(exc, "HTTPNotFound")
        assert hasattr(exc, "HTTPBadRequest")
        assert hasattr(exc, "HTTPUnauthorized")
        assert hasattr(exc, "HTTPForbidden")
        assert hasattr(exc, "HTTPInternalServerError")

    def test_all_exports_match_globals(self):
        """__all__ should list every generated class."""
        for name in exc.__all__:
            assert hasattr(exc, name), f"{name} in __all__ but not in module"

    def test_classes_are_subclasses_of_httperror(self):
        """Each generated class should inherit from HTTPError."""
        for name in exc.__all__:
            cls = getattr(exc, name)
            assert issubclass(cls, HTTPError), f"{name} is not an HTTPError subclass"

    def test_instantiation_defaults(self):
        """Instantiate HTTPNotFound with defaults and verify status/title."""
        error = exc.HTTPNotFound()
        assert error.status == "404 Not Found"
        assert error.title == "404 Not Found"
        assert error.description is None

    def test_instantiation_custom_fields(self):
        """Custom title and description should be set."""
        error = exc.HTTPBadRequest(
            title="Validation Failed",
            description="Name field is required",
        )
        assert error.status == "400 Bad Request"
        assert error.title == "Validation Failed"
        assert error.description == "Name field is required"

    def test_instantiation_with_headers(self):
        """Headers should be passed through."""
        error = exc.HTTPUnauthorized(headers={"WWW-Authenticate": "Bearer"})
        assert error.status == "401 Unauthorized"

    def test_only_4xx_and_5xx_generated(self):
        """No 1xx, 2xx, or 3xx classes should be generated."""
        for name in exc.__all__:
            cls = getattr(exc, name)
            instance = cls()
            code = int(instance.status.split()[0])
            assert code >= 400, f"{name} has unexpected status code {code}"

    def test_docstrings_are_set(self):
        """Each class should have a docstring derived from the HTTP message."""
        for name in exc.__all__:
            cls = getattr(exc, name)
            assert cls.__doc__ is not None, f"{name} is missing a docstring"
            assert cls.__doc__.endswith("."), f"{name} docstring should end with a period"
