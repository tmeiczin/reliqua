"""Tests for reliqua.auth module."""

import base64
from unittest.mock import MagicMock

import falcon
import pytest

from reliqua.auth import (
    AccessCallback,
    AccessList,
    AccessMap,
    AccessResource,
    AuthenticationContext,
    AuthMiddleware,
    BasicAuthentication,
    MultiAuthentication,
    is_base64,
)


class TestIsBase64:
    """Tests for is_base64 helper."""

    def test_valid_base64(self):
        assert is_base64("aGVsbG8=") is True

    def test_invalid_base64(self):
        assert is_base64("not-base64!!!") is False

    def test_empty_string(self):
        assert is_base64("") is True


class TestAuthenticationContext:
    """Tests for AuthenticationContext."""

    def test_default_role_is_none(self):
        ctx = AuthenticationContext()
        assert ctx.role is None

    def test_kwargs_set_attributes(self):
        ctx = AuthenticationContext(user="alice", role="admin")
        assert ctx.user == "alice"
        assert ctx.role == "admin"


class TestAccessList:
    """Tests for AccessList access control."""

    def test_init_with_none_defaults(self):
        """Should not crash when routes/methods are None."""
        ac = AccessList()
        assert ac.routes == []
        assert ac.methods == []

    def test_init_with_values(self):
        ac = AccessList(routes=["/users", "/Admin"], methods=["GET", "POST"])
        assert ac.routes == ["/users", "/admin"]
        assert ac.methods == ["get", "post"]

    def test_allow_mode_matched_route_requires_auth(self):
        """In allow mode, listed routes require authentication."""
        ac = AccessList(routes=["/secret"], methods=[], default_mode="allow")
        assert ac.authentication_required("/secret", "GET", None) is True

    def test_allow_mode_unmatched_route_no_auth(self):
        """In allow mode, unlisted routes do NOT require authentication."""
        ac = AccessList(routes=["/secret"], methods=[], default_mode="allow")
        assert ac.authentication_required("/public", "GET", None) is False

    def test_allow_mode_matched_method_requires_auth(self):
        """In allow mode, listed methods require authentication."""
        ac = AccessList(routes=[], methods=["post"], default_mode="allow")
        assert ac.authentication_required("/any", "POST", None) is True

    def test_deny_mode_matched_route_no_auth(self):
        """In deny mode, listed routes are exempt from auth."""
        ac = AccessList(routes=["/public"], methods=[], default_mode="deny")
        assert ac.authentication_required("/public", "GET", None) is False

    def test_deny_mode_unmatched_route_requires_auth(self):
        """In deny mode, unlisted routes require authentication."""
        ac = AccessList(routes=["/public"], methods=[], default_mode="deny")
        assert ac.authentication_required("/secret", "GET", None) is True

    def test_authorized_not_implemented(self):
        ac = AccessList()
        with pytest.raises(NotImplementedError):
            ac.authorized(None, None, None, None)


class TestAccessCallback:
    """Tests for AccessCallback access control."""

    def test_authorized_delegates_to_callback(self):
        callback = MagicMock(return_value=True)
        ac = AccessCallback(authenticate_callback=MagicMock(), authorized_callback=callback)
        ctx = AuthenticationContext(role="admin")
        assert ac.authorized(ctx, "/users", "GET", None) is True
        callback.assert_called_once_with(ctx, "/users", "GET")

    def test_authentication_required_delegates_to_callback(self):
        callback = MagicMock(return_value=True)
        ac = AccessCallback(authenticate_callback=callback, authorized_callback=MagicMock())
        assert ac.authentication_required("/users", "GET", None) is True
        callback.assert_called_once_with(route="/users", method="GET")


class TestAccessMap:
    """Tests for AccessMap access control."""

    ac = None
    access_map = None

    def setup_method(self):
        self.access_map = {
            "/users": {
                "GET": ["admin", "user"],
                "POST": ["admin"],
            },
            "/public": {
                "*": ["*"],
            },
        }
        self.ac = AccessMap(self.access_map)

    def test_authorized_with_valid_role(self):
        ctx = AuthenticationContext(role="admin")
        assert self.ac.authorized(ctx, "/users", "GET", None) is True

    def test_authorized_with_invalid_role(self):
        ctx = AuthenticationContext(role="guest")
        assert self.ac.authorized(ctx, "/users", "GET", None) is False

    def test_authorized_wildcard_role(self):
        ctx = AuthenticationContext(role="anyone")
        assert self.ac.authorized(ctx, "/public", "GET", None) is True

    def test_authorized_missing_route_returns_false(self):
        """Missing routes should return False, not crash."""
        ctx = AuthenticationContext(role="admin")
        assert self.ac.authorized(ctx, "/nonexistent", "GET", None) is False

    def test_authentication_required_normal_route(self):
        assert self.ac.authentication_required("/users", "GET", None) is True

    def test_authentication_not_required_wildcard(self):
        assert self.ac.authentication_required("/public", "GET", None) is False

    def test_authentication_required_missing_route(self):
        """Missing routes should require authentication, not crash."""
        assert self.ac.authentication_required("/nonexistent", "GET", None) is True


class TestAccessResource:
    """Tests for AccessResource access control."""

    def _make_resource(self, auth_dict=None):
        resource = MagicMock()
        resource.name = "TestResource"
        if auth_dict is not None:
            resource.__auth__ = auth_dict
        else:
            del resource.__auth__
        return resource

    def test_authorized_with_matching_role(self):
        ac = AccessResource()
        resource = self._make_resource({"GET": ["admin"]})
        ctx = AuthenticationContext(role="admin")
        assert ac.authorized(ctx, "/test", "GET", resource) is True

    def test_authorized_with_wrong_role(self):
        ac = AccessResource()
        resource = self._make_resource({"GET": ["admin"]})
        ctx = AuthenticationContext(role="guest")
        assert ac.authorized(ctx, "/test", "GET", resource) is False

    def test_authorized_wildcard_method(self):
        ac = AccessResource()
        resource = self._make_resource({"*": ["admin"]})
        ctx = AuthenticationContext(role="admin")
        assert ac.authorized(ctx, "/test", "GET", resource) is True

    def test_authorized_no_auth_defined_allows(self):
        ac = AccessResource()
        resource = self._make_resource({})
        ctx = AuthenticationContext(role="admin")
        assert ac.authorized(ctx, "/test", "GET", resource) is True

    def test_authorized_no_auth_raises_when_configured(self):
        ac = AccessResource(raise_on_undefined=True)
        resource = self._make_resource({})
        ctx = AuthenticationContext(role="admin")
        with pytest.raises(falcon.HTTPNotImplemented):
            ac.authorized(ctx, "/test", "GET", resource)

    def test_authorized_case_insensitive_method(self):
        """Authorized should find roles regardless of method case."""
        ac = AccessResource()
        resource = self._make_resource({"GET": ["admin"]})
        ctx = AuthenticationContext(role="admin")
        # method passed as lowercase should match "GET" key
        assert ac.authorized(ctx, "/test", "get", resource) is True

    def test_authentication_required_deny_mode_with_roles(self):
        ac = AccessResource(default_mode="deny")
        resource = self._make_resource({"GET": ["admin"]})
        assert ac.authentication_required("/test", "GET", resource) is True

    def test_authentication_required_allow_mode_no_roles(self):
        ac = AccessResource(default_mode="allow")
        resource = self._make_resource({})
        assert ac.authentication_required("/test", "GET", resource) is False

    def test_authentication_required_deny_mode_no_roles(self):
        ac = AccessResource(default_mode="deny")
        resource = self._make_resource({})
        assert ac.authentication_required("/test", "GET", resource) is True


class TestBasicAuthentication:
    """Tests for BasicAuthentication."""

    def test_authenticate_success(self):
        auth = BasicAuthentication(validation=lambda u, p: AuthenticationContext(user=u, role="admin"))
        token = base64.b64encode(b"alice:secret").decode("utf-8")
        req = MagicMock()
        req.get_header.return_value = f"Basic {token}"
        result = auth.authenticate(req, None, None)
        assert result.user == "alice"

    def test_authenticate_missing_header_raises(self):
        auth = BasicAuthentication(validation=lambda u, p: None)
        req = MagicMock()
        req.get_header.return_value = None
        with pytest.raises(falcon.HTTPUnauthorized):
            auth.authenticate(req, None, None)

    def test_authenticate_invalid_credentials_raises(self):
        auth = BasicAuthentication(validation=lambda u, p: None)
        token = base64.b64encode(b"bad:creds").decode("utf-8")
        req = MagicMock()
        req.get_header.return_value = f"Basic {token}"
        with pytest.raises(falcon.HTTPUnauthorized):
            auth.authenticate(req, None, None)

    def test_dict_returns_openapi_schema(self):
        auth = BasicAuthentication(validation=lambda u, p: None)
        schema = auth.dict()
        assert "BasicAuthentication" in schema
        assert schema["BasicAuthentication"]["type"] == "http"
        assert schema["BasicAuthentication"]["scheme"] == "basic"


class TestMultiAuthentication:
    """Tests for MultiAuthentication."""

    def test_first_authenticator_succeeds(self):
        auth1 = MagicMock()
        auth1.authenticate.return_value = AuthenticationContext(role="admin")
        auth2 = MagicMock()
        multi = MultiAuthentication([auth1, auth2])
        result = multi.authenticate(None, None, None)
        assert result.role == "admin"
        auth2.authenticate.assert_not_called()

    def test_falls_through_on_failure(self):
        auth1 = MagicMock()
        auth1.authenticate.side_effect = falcon.HTTPUnauthorized(description="fail")
        auth2 = MagicMock()
        auth2.authenticate.return_value = AuthenticationContext(role="user")
        multi = MultiAuthentication([auth1, auth2])
        result = multi.authenticate(None, None, None)
        assert result.role == "user"

    def test_all_fail_raises(self):
        auth1 = MagicMock()
        auth1.authenticate.side_effect = falcon.HTTPUnauthorized(description="fail")
        auth2 = MagicMock()
        auth2.authenticate.side_effect = falcon.HTTPUnauthorized(description="fail")
        multi = MultiAuthentication([auth1, auth2])
        with pytest.raises(falcon.HTTPUnauthorized):
            multi.authenticate(None, None, None)

    def test_dict_merges_schemas(self):
        auth1 = MagicMock()
        auth1.dict.return_value = {"BasicAuth": {"type": "http"}}
        auth2 = MagicMock()
        auth2.dict.return_value = {"ApiKey": {"type": "apiKey"}}
        multi = MultiAuthentication([auth1, auth2])
        schema = multi.dict()
        assert "BasicAuth" in schema
        assert "ApiKey" in schema


class TestAuthMiddleware:
    """Tests for AuthMiddleware."""

    def test_skips_no_auth_resource(self):
        """Resources with no_auth=True should never be authenticated."""
        auth = MagicMock()
        control = MagicMock()
        mw = AuthMiddleware([auth], control=control)

        resource = MagicMock()
        resource.no_auth = True

        mw.process_resource(MagicMock(), MagicMock(), resource, {})
        control.authentication_required.assert_not_called()

    def test_skips_when_auth_not_required(self):
        auth = MagicMock()
        control = MagicMock()
        control.authentication_required.return_value = False
        mw = AuthMiddleware([auth], control=control)

        resource = MagicMock(spec=[])  # no no_auth attribute
        req = MagicMock()
        req.uri_template = "/public"
        req.method = "GET"

        mw.process_resource(req, MagicMock(), resource, {})
        auth.authenticate.assert_not_called()

    def test_unauthorized_role_raises(self):
        auth_obj = MagicMock()
        ctx = AuthenticationContext(role="guest")
        auth_obj.authenticate.return_value = ctx

        control = MagicMock()
        control.authentication_required.return_value = True
        control.authorized.return_value = False

        mw = AuthMiddleware([auth_obj], control=control)

        resource = MagicMock(spec=[])
        req = MagicMock()
        req.uri_template = "/secret"
        req.method = "DELETE"
        req.context = {}

        with pytest.raises(falcon.HTTPUnauthorized):
            mw.process_resource(req, MagicMock(), resource, {})
