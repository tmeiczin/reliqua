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
    expected to implement all logic and an `exempt` method which
    is called by the Auth instance.
    """

    def exempt(self, _route, _method, _resource):
        """Return whether authentication is required."""
        raise NotImplementedError("authenticate method not implemented")


class AccessCallback:
    """
    Access callback.

    Access control is checked by calling a user defined method. The called method
    will be supplied the Endpoint, Route, and HTTP method. The called method
    must return `True` or `False`.
    """

    def __init__(self, callback):
        """
        Create the AccessCallback instance.

        :param callable callback:  Callback method
        :return:
        """
        self.callback = callback

    def exempt(self, route, method, _resource):
        """
        Return whether the route or method is exempt.

        Return whether the route or method is exempt from requiring
        authentication by calling the callback method.

        :param str route:    The route being called
        :param str method:   The http method invoked
        :return bool:        True if exempt
        """
        return self.callback(route=route, method=method)


class AccessList:
    """
    Access List.

    Access control is checked by the routes and/or method specified in the
    the exempt lists.
    """

    def __init__(self, routes=None, methods=None):
        """
        Create the AccessList instance.

        :param list routes:     List of exempt routes
        :param list methods:    List of exempt methods
        """
        self.routes = [x.lower() for x in routes]
        self.methods = [x.lower() for x in methods]

    def exempt(self, route, method, _resource):
        """
        Return whether the route or method is exempt.

        Return whether the route or method is exempt from requiring
        authentication by comparing the route and method against the
        exempts lists.

        :param str route:    The route being called
        :param str method:   The http method invoked
        :return bool:        True if exempt
        """
        if route.lower() in self.routes or method.lower() in self.methods:
            return True

        return False


class AccessResource:
    """
    Access Resource.

    Access control is checked at the resource level. The resource defines
    which actions require authentication.
    """

    def exempt(self, _route, method, resource):
        """
        Return whether the route or method is exempt.

        Return whether the route or method is exempt from requiring
        authentication by checking the resource itself.

        :param str method:          The http method invoked
        :param Resource resource:   The resource
        :return bool:               True if exempt
        """
        auth = getattr(resource, "__auth_actions__", [])
        methods = [x.lower() for x in auth]

        if method.lower() not in methods:
            return True

        return False


class Auth:
    """Auth abstract base class."""

    control = AccessControl()

    @property
    def name(self):
        """Return auth name."""
        return self.__class__.__name__

    def authenticate(self, _req, _resp, _resource):
        """Return whether client is authenticated."""
        raise NotImplementedError("authenticate method not implemented")

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
        if self.control.exempt(req.uri_template, req.method, resource):
            return

        req.context["user"] = self.authenticate(req, resp, resource)


class ApiAuth(Auth):
    """API Authentication."""

    location = " any"

    def __init__(self, name, description=None, validation=None, control=None):
        """
        Create an API authentication instance.

        :param str name:        Parameter name
        :param description:     Description
        :return:
        """
        self.kind = "apiKey"
        self.parameter_name = name
        self.description = description
        self.validation = validation
        self.control = control

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


class CookieAuth(ApiAuth):
    """Cookie Authentication."""

    location = "cookie"

    def authenticate(self, req, _resp, _resource):
        """Return whether client is authenticated."""
        api_key = req.get_cookie_values(self.parameter_name)
        if api_key:
            api_key = api_key[0]

        print(f"cookie {api_key}")
        if not self.validation(api_key):
            raise falcon.HTTPUnauthorized(description="Invalid authorization")

        return True


class HeaderAuth(ApiAuth):
    """Header Authentication."""

    location = "header"

    def authenticate(self, req, _resp, _resource):
        """Return whether client is authenticated."""
        api_key = req.get_header(self.parameter_name)

        if not self.validation(api_key):
            raise falcon.HTTPUnauthorized(description="Invalid authorization")

        return True


class QueryAuth(ApiAuth):
    """Query Authentication."""

    location = "query"

    def authenticate(self, req, _resp, _resource):
        """Return whether client is authenticated."""
        api_key = req.params.get(self.parameter_name)

        if not self.validation(api_key):
            raise falcon.HTTPUnauthorized(description="Invalid authorization")

        return True


class BasicAuth(Auth):
    """Basic Authentication."""

    def __init__(self, validation=None, control=None):
        """
        Create BasicAuth instance.

        :param callable validation:       Callback to validate credentials
        :param AccessControl control:     Access control class
        :return:
        """
        self.kind = "http"
        self.scheme = "basic"
        self.validation = validation
        self.control = control

    @property
    def name(self):
        """Return auth name."""
        return self.__class__.__name__

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
        if not self.validation(username, password):
            raise falcon.HTTPUnauthorized(description="Invalid authorization")

        return True


class BearerAuth(Auth):
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


class MultiAuth(Auth):
    """
    MultiAuth class.

    MultiAuth allows you to specify multiple auth mechanisms. They
    will then be iterated until one if successful
    """

    def __init__(self, authenticators, control=None):
        """
        Create a MultiAuth instance.

        :param list[Auth] auth:    A list of Authenticators
        :return bool:               True if authenticated
        """
        self.authenticators = authenticators
        self.control = control

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
