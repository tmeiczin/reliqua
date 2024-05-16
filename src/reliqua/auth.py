"""
Reliqua Framework.

Copyright 2016-2024.
"""

import base64
import re

import falcon


def is_base64(data):
    """
    Return if string is base64.

    Check if string is base64 encoded.

    :param str data:     Base64 string
    :return bool:        True is base64
    """
    try:
        base64.b64decode(data).decode("utf-8")
    except (base64.binascii.Error, UnicodeDecodeError):
        return False

    return True


class AccessControl:
    """
    Access control class.

    The abstract base class for access control. The subclass is
    expected to implement all logic.

    The `authentication_required` method returns whether a call
    requires authentication.

    The `authorized` method returns whether the client is authorized
    to execute the call.
    """

    def authorized(self, role, _route, _method, _resource):
        """Return whether client is allowed to access resource."""
        raise NotImplementedError("authorized method not implemented")

    def authentication_required(self, _route, _method, _resource):
        """Return whether authentication is required."""
        raise NotImplementedError("authentication required method not implemented")


class AccessCallback(AccessControl):
    """
    Access callback.

    Access control is checked by calling a user defined methods. The called method
    will be supplied the endpoint, route, and HTTP method. The called method
    must return `True` or `False`.
    """

    def __init__(self, authenticate_callback, authorized_callback):
        """
        Create the AccessCallback instance.

        :param callable callback:  Callback method
        :return:
        """
        self.authenticate_callback = authenticate_callback
        self.authorized_callback = authorized_callback

    def authorized(self, role, route, method, _resource):
        """
        Return whether the route or method is authorized.

        Return whether the route or method is allowed for the
        given role.

        :param str role:     Role of client
        :param str route:    Route being called
        :param str method:   HTTP method invoked
        :return bool:        True if authorized
        """
        return self.authorized_callback(role, route, method)

    def authentication_required(self, route, method, _resource):
        """
        Return whether the route or method is exempt.

        Return whether the route or method requires
        authentication by calling the callback method.

        :param str route:    Route being called
        :param str method:   HTTP method invoked
        :return bool:        True if authentication is required
        """
        return self.authenticate_callback(route=route, method=method)


class AccessList(AccessControl):
    """
    Access List.

    Access control is checked by the routes and/or method specified in
    simple lists. If default mode is allow, then only routes/methods specified
    will required authentication. If default mode is deny, then only the
    routes/specified will be exempted.
    """

    def __init__(self, routes=None, methods=None, default_mode="allow"):
        """
        Create the AccessList instance.

        :param list routes:        List of routes to apply rules
        :param list methods:       List of methods to apply rules
        :param str default_mode:   Default mode (allow|deny)
        """
        self.routes = [x.lower() for x in routes]
        self.methods = [x.lower() for x in methods]
        self.default_mode = default_mode

    def authorized(self, role, _route, _method, _resource):
        """Return whether client is allowed to access resource."""
        raise NotImplementedError("authorized method not implemented")

    def authentication_required(self, route, method, _resource):
        """
        Return whether the route or method requires authentication.

        Return whether the route or method requires authentication
        by comparing the route or method against the rule lists.

        :param str route:    Route being called
        :param str method:   HTTP method invoked
        :return bool:        True if authentication is required
        """
        matched = False
        required = self.default_mode != "allowed"

        if route.lower() in self.routes or method.lower() in self.methods:
            matched = True

        # check if authentication is required
        if self.default_mode == "allow":
            # if default mode is allow, then a match means auth required
            required = not matched
        else:
            # default mode is deny, then a match means auth not required
            required = matched

        return required


class AccessMap(AccessControl):
    """
    Access Map.

    Access control is checked by the routes and/or method specified in the
    the dictionary. Only items defined will be checked and everything else will
    be denied. Therefore, this must be a complete map.

    The access map follows the form:

    route: {
        http_method: [roles]
    }

    Example:

    "/users": {
        "GET": ["admin", "user"]
    }

    You can use "*" to apply the access to all http methods.

    You can add "*" to the roles list to exempt the
    route/method from requiring authentication.
    """

    def __init__(self, access_map):
        """
        Create the AccessList instance.

        :param list access_map:    Dictionary of rules
        :return:
        """
        self.access_map = access_map

    def authorized(self, role, route, method, _resource):
        """
        Return whether client is allowed to access resource.

        :param str role:     Client role
        :param str route:    Route being called
        :param str method:   HTTP method being invoked
        :return bool:        True if authorized
        """
        route = self.access_map.get(route)
        roles = route.get("*") or route.get(method)
        if role in roles or "*" in roles:
            return True

        return False

    def authentication_required(self, route, method, _resource):
        """
        Return whether the route/method requires authentication.

        Return whether the route or method requires authentication
        by checking the resource auth dictionary.

        :param str route:    The route being called
        :param str method:   The http method invoked
        :return bool:        True if e
        """
        route = self.access_map.get(route)
        roles = route.get("*") or route.get(method)

        # if method is specified and has a wildcard role
        # then authentication is not required
        if roles and "*" in roles:
            return False

        return True


class AccessResource(AccessControl):
    """
    Access Resource Map.

    Access control is checked by the routes and/or methods specified in the resource.
    If the default mode is `allow` then routes or actions with no definition will be allowed.
    When the default mode is `deny`, then all undefine routes and methods will be denied.

    The resource map follows the form:

    __auth__: {
        http_method: [roles]
    }

    Example:

    __auth__: {
        "GET": ["admin", "user"]
    }

    You can use "*" to apply the access to all http methods.

    You can add "*" to the roles list or set roles to an empty list
    to exempt the route/method from requiring authentication.
    """

    def __init__(self, default_mode="deny", raise_on_undefined=False):
        """
        Create the AccessList instance.

        :param str default_mode:         Default mode (allow|deny)
        :param bool raise_on_undefined:  If a resource has undefined auth attributes, raise exception
        :return:
        """
        self.default_mode = default_mode
        self.raise_on_undefined = raise_on_undefined

    def authorized(self, role, _route, method, resource):
        """
        Return whether client is allowed to access resource.

        :param str role:             Client role
        :param str method:           HTTP method being invoked
        :param Resource resource:    Route resource
        :return bool:                True if authorized
        """
        auth = getattr(resource, "__auth__", {})
        roles = auth.get("*", []) or auth.get(method, [])

        # if no roles are defined skip authorization
        # or raise an exception
        if not roles:
            if self.raise_on_undefined:
                raise falcon.HTTPNotImplemented(f"no roles are defined for {resource.name} {method}")

            return True

        if role in roles or "*" in roles:
            return True

        return False

    def authentication_required(self, _route, method, resource):
        """
        Return whether the route or method requires authentication.

        Return whether the route or method for the resource requires
        authentication by comparing the route and method against the
        resources dictionary.

        :param str method:   HTTP method invoked
        :param Resource resource:    Route resource
        :return bool:       True if authentication is required
        """
        auth = getattr(resource, "__auth__", {})
        roles = auth.get(method.lower(), []) or auth.get(method.upper(), []) or auth.get("*", [])

        # If no roles are defined and default mode is allow
        # then no authentication is required.
        if not roles and self.default_mode == "allow":
            return False

        return True


class Authentication:
    """Authentication abstract base class."""

    @property
    def name(self):
        """Return authentication name."""
        return self.__class__.__name__

    def authenticate(self, _req, _resp, _resource):
        """Return whether client is authenticated."""
        raise NotImplementedError("authenticate method not implemented")


class ApiAuthentication(Authentication):
    """
    API Authentication.

    An abstract base class for API key type authentications.
    """

    location = " any"

    def __init__(self, name, description=None, validation=None):
        """
        Create an API authentication instance.

        :param str name:             Parameter name
        :param str description:      Description
        :param callable validation:  Validation callback
        :return:
        """
        self.kind = "apiKey"
        self.parameter_name = name
        self.description = description
        self.validation = validation

    @property
    def name(self):
        """Return auth name."""
        return self.__class__.__name__

    def authenticate(self, _req, _resp, resource):
        """Return whether client is authenticated."""
        raise NotImplementedError("authenticate method not implemented")

    def dict(self):
        """Return OpenAPI Schema."""
        return {
            self.name: {
                "type": self.kind,
                "name": self.parameter_name,
                "in": self.location,
                "description": self.description,
            }
        }


class CookieAuthentication(ApiAuthentication):
    """
    Cookie Authentication.

    This class provides cookie authentication. The caller must provide a
    validation callback which accepts token and returns
    user string. Any False like value will raise an error.
    """

    location = "cookie"

    def validate(self, token):
        """
        Validate the user.

        :param str token:       Client token
        :return str:            Username

        This method must be passed in during instantiation.
        """
        raise NotImplementedError("authenticate method not implemented")

    def authenticate(self, req, _resp, _resource):
        """Return whether client is authenticated."""
        api_key = req.get_cookie_values(self.parameter_name)
        if api_key:
            api_key = api_key[0]

        username = self.validation(api_key)
        if not username:
            raise falcon.HTTPUnauthorized(description="Invalid cookie authorization")

        return username


class HeaderAuthentication(ApiAuthentication):
    """
    Header Authentication.

    This class provides header authentication. The caller must provide a
    validation callback which accepts token and returns
    user string. Any False like value will raise an error.
    """

    location = "header"

    def validate(self, token):
        """
        Validate the user.

        :param str token:       Client token
        :return str:            Username

        This method must be passed in during instantiation.
        """
        raise NotImplementedError("authenticate method not implemented")

    def authenticate(self, req, _resp, _resource):
        """Return whether client is authenticated."""
        api_key = req.get_header(self.parameter_name)

        username = self.validation(api_key)
        if not username:
            raise falcon.HTTPUnauthorized(description="Invalid header authorization")

        return username


class QueryAuthentication(ApiAuthentication):
    """
    Query Authentication.

    This class provides query parameter authentication. The caller must provide a
    validation callback which accepts token and returns
    user string. Any False like value will raise an error.
    """

    location = "query"

    def validate(self, token):
        """
        Validate the user.

        :param str token:       Client token
        :return str:            Username

        This method must be passed in during instantiation.
        """
        raise NotImplementedError("authenticate method not implemented")

    def authenticate(self, req, _resp, _resource):
        """Return whether client is authenticated."""
        api_key = req.params.get(self.parameter_name)

        username = self.validation(api_key)
        if not username:
            raise falcon.HTTPUnauthorized(description="Invalid query authorization")

        return username


class BasicAuthentication(Authentication):
    """
    Basic Authentication.

    This class provides Basic authentication. The caller must provide a
    validation callback which accepts a username and password and returns
    user string. Any False like value will raise an error.
    """

    def __init__(self, validation=None):
        """
        Create BasicAuth instance.

        :param callable validation:       Callback to validate credentials
        :param AccessControl control:     Access control class
        :return:
        """
        self.kind = "http"
        self.scheme = "basic"
        self.validation = validation

    @property
    def name(self):
        """Return auth name."""
        return self.__class__.__name__

    def validate(self, username, password):
        """
        Validate the user.

        :param str username:    Client username
        :param str password:    Client password
        :return str:            Username

        This method must be passed in during instantiation.
        """
        raise NotImplementedError("authenticate method not implemented")

    def dict(self):
        """Return OpenAPI Schema."""
        return {
            self.name: {
                "type": self.kind,
                "scheme": self.scheme,
            },
        }

    def _credentials(self, req):
        header = req.get_header("Authorization")
        if not header:
            raise falcon.HTTPUnauthorized(description="Missing Authorization Header")

        m = re.search(r"Basic ([-A-Za-z0-9+/=]+)", header)
        if not m:
            raise falcon.HTTPUnauthorized(description=f"Invalid Authorization Header {header}")

        token = m.group(1)

        if not is_base64(token):
            raise falcon.HTTPUnauthorized(description="Invalid Token")

        username, _, password = base64.b64decode(token).decode("utf-8").partition(":")

        return username, password

    def authenticate(self, req, _resp, _resource):
        """
        Authenticate user.

        Authenticate with the credentials

        :return bool:     True if authenticated
        """
        username, password = self._credentials(req)

        username = self.validation(username, password)
        if not username:
            raise falcon.HTTPUnauthorized(description="Invalid authorization")

        return username


class BearerAuthentication(Authentication):
    """Bearer Token Authentication."""

    def __init__(self):
        """
        Create BearerAuth instance.

        :return:
        """
        self.kind = "http"
        self.scheme = "bearer"

    @property
    def name(self):
        """Return auth name."""
        return self.__class__.__name__

    def authenticate(self, _req, _resp, _resource):
        """Return whether client is authenticated."""
        raise NotImplementedError("authenticate method not implemented")

    def dict(self):
        """Return OpenAPI Schema."""
        return {
            self.name: {
                "type": self.kind,
                "scheme": self.scheme,
            }
        }


class MultiAuthentication(Authentication):
    """
    MultiAuth class.

    MultiAuth allows you to specify multiple auth mechanisms. They
    will then be iterated until one is successful. The access control
    specified will override any of the individual authentications.
    """

    def __init__(self, authenticators):
        """
        Create a MultiAuth instance.

        :param list[Auth] auth:    A list of Authenticators
        :return bool:               True if authenticated
        """
        self.authenticators = authenticators

    def authenticate(self, request, response, resource):
        """
        Authenticate user.

        Authenticate with the credentials

        :return bool:        True if authenticated
        """
        for auth in self.authenticators:
            try:
                return auth.authenticate(request, response, resource)
            except falcon.HTTPUnauthorized:
                pass

        raise falcon.HTTPUnauthorized(description="Invalid authorization")

    def dict(self):
        """Return OpenAPI Schema."""
        schema = {}
        for auth in self.authenticators:
            schema.update(auth.dict())

        return schema


class AuthMiddleware:
    """Auth middleware."""

    def __init__(self, authenticators, control=None):
        """
        Create a MultiAuth instance.

        :param list[Auth] auth:    A list of Authenticators
        :return bool:               True if authenticated
        """
        self.authenticators = authenticators
        self.control = control

    def dict(self):
        """Return OpenAPI Schema."""
        schema = {}
        for auth in self.authenticators:
            schema.update(auth.dict())

        return schema

    def authenticate(self, request, response, resource):
        """
        Authenticate user.

        Authenticate with the credentials

        :return bool:        True if authenticated
        """
        for auth in self.authenticators:
            try:
                return auth.authenticate(request, response, resource)
            except falcon.HTTPUnauthorized:
                pass

        raise falcon.HTTPUnauthorized(description="Invalid authorization")

    def process_resource(self, req, resp, resource, _params):
        """
        Process request after routing.

        Process the http resource. This method is called if the
        request was routed to a resource. If the user is authenticated,
        the user key will be added/set in the request context.

        :param Request req:          Request object
        :param Response resp:        Response object
        :param Resource resource:    Resource object
        :param dict params:          Additional parameters from the URI
        :return:
        """
        user = None
        authorized = False

        # if resource has explicit no_auth, always skip
        # authentication.
        if getattr(resource, "no_auth", False):
            return

        # check if request requires authentication
        if not self.control.authentication_required(req.uri_template, req.method, resource):
            return

        # authenticate user
        user, *role = self.authenticate(req, resp, resource)
        role = role[0] if role else None

        # if a role is returned check if authorized
        if role:
            authorized = self.control.authorized(role, req.uri_template, req.method, resource)
            if not authorized:
                raise falcon.HTTPUnauthorized(
                    description=f"role {role} is not authorized to {req.method} {req.uri_template}"
                )

        req.context["role"] = role
        req.context["authorized"] = authorized
        req.context["user"] = user
