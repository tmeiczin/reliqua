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

import re

from falcon.http_error import HTTPError

from .status_codes import CODES

# Map of HTTP status codes (4xx and 5xx) to exception class names.
#
# Each entry generates a class like:
#
#   class HTTPNotFound(HTTPError):
#       """Not Found."""
#       def __init__(self, title=None, description=None, headers=None):
#           ...
#
# The classes are added to this module's namespace and __all__,
# so they can be imported normally:
#
#   from reliqua.exceptions import HTTPNotFound

_ERROR_CODES = {code: message for code, message in CODES.items() if int(code) >= 400}


def _make_class_name(message):
    """Convert an HTTP message to a PascalCase class name prefixed with HTTP."""
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", message)
    return "HTTP" + cleaned.replace(" ", "")


def _make_exception_class(code, message):
    """Dynamically create an HTTPError subclass for the given status code."""
    status_string = f"{code} {message}"

    def _init(self, title=None, description=None, headers=None):
        """Initialize."""
        super(self.__class__, self).__init__(
            status=status_string,
            title=title or status_string,
            description=description,
            headers=headers,
        )

    return type(
        _make_class_name(message),
        (HTTPError,),
        {"__doc__": f"{message}.", "__init__": _init},
    )


# Generate all exception classes and populate __all__
__all__ = []

for _code, _message in _ERROR_CODES.items():
    _cls_name = _make_class_name(_message)
    _cls = _make_exception_class(_code, _message)
    globals()[_cls_name] = _cls
    __all__ += [_cls_name]  # noqa: PLE0604
