"""
MIT License.

Copyright (c) 2017 Terrence Meiczinger

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from falcon.http_error import HTTPError


class HTTPBadRequest(HTTPError):
    """Bad Request."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "400 Bad Request"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPUnauthorized(HTTPError):
    """Unauthorized."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "401 Unauthorized"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPPaymentRequired(HTTPError):
    """Payment Required."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "402 Payment Required"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPForbidden(HTTPError):
    """Forbidden."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "403 Forbidden"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPNotFound(HTTPError):
    """Not Found."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "404 Not Found"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPMethodNotAllowed(HTTPError):
    """Method Not Allowed."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "405 Method Not Allowed"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPNotAcceptable(HTTPError):
    """Not Acceptable."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "406 Not Acceptable"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPProxyAuthenticationRequired(HTTPError):
    """Proxy Authentication Required."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "407 Proxy Authentication Required"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPRequestTimeout(HTTPError):
    """Request Timeout."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "408 Request Timeout"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPConflict(HTTPError):
    """Conflict."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "409 Conflict"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPGone(HTTPError):
    """Gone."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "410 Gone"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPLengthRequired(HTTPError):
    """Length Required."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "411 Length Required"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPPreconditionFailed(HTTPError):
    """Precondition Failed."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "412 Precondition Failed"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPPayloadTooLarge(HTTPError):
    """Payload Too Large."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "413 Payload Too Large"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPUnsupportedMediaType(HTTPError):
    """Unsupported Media Type."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "415 Unsupported Media Type"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPRangeNotSatisfiable(HTTPError):
    """Range Not Satisfiable."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "416 Range Not Satisfiable"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPExpectationFailed(HTTPError):
    """Expectation Failed."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "417 Expectation Failed"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPUnprocessableEntity(HTTPError):
    """Unprocessable Entity."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "422 Unprocessable Entity"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPLocked(HTTPError):
    """Locked."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "423 Locked"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPFailedDependency(HTTPError):
    """Failed Dependency."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "424 Failed Dependency"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPUpgradeRequired(HTTPError):
    """Upgrade Required."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "426 Upgrade Required"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPPreconditionRequired(HTTPError):
    """Precondition Required."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "428 Precondition Required"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPTooManyRequests(HTTPError):
    """Too Many Requests."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "429 Too Many Requests"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPRequestHeaderFieldsTooLarge(HTTPError):
    """Request Header Fields Too Large."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "431 Request Header Fields Too Large"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPUnavailableForLegalReasons(HTTPError):
    """Unavailable For Legal Reasons."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "451 Unavailable For Legal Reasons"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPInternalServerError(HTTPError):
    """Internal Server Error."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "500 Internal Server Error"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPNotImplemented(HTTPError):
    """Not Implemented."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "501 Not Implemented"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPBadGateway(HTTPError):
    """Bad Gateway."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "502 Bad Gateway"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPServiceUnavailable(HTTPError):
    """Service Unavailable."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "503 Service Unavailable"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPGatewayTimeout(HTTPError):
    """Gateway Timeout."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "504 Gateway Timeout"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPVersionNotSupported(HTTPError):
    """HTTP Version Not Supported."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "505 HTTP Version Not Supported"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPInsufficientStorage(HTTPError):
    """Insufficient Storage."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "507 Insufficient Storage"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPLoopDetected(HTTPError):
    """Loop Detected."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "508 Loop Detected"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )


class HTTPNetworkAuthenticationRequired(HTTPError):
    """Network Authentication Required."""

    def __init__(self, title=None, description=None, headers=None):
        """Initialize."""
        status = "511 Network Authentication Required"
        title = title or status

        super().__init__(
            status=status,
            title=title,
            description=description,
            headers=headers,
        )
