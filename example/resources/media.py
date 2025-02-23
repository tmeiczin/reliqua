"""
Reliqua Framework.

Copyright 2016-2024.
"""

import os

from reliqua.resources.base import Resource
from reliqua.status_codes import HTTP


class Gzip(Resource):
    """GZIP resource."""

    __routes__ = {
        "/gzip": {},
    }

    def on_get(self, _req, resp):
        """
        Send contact message.

        :accepts json:          Accepts JSON
        :response 200 binary:   All good
        :return gzip:           Return data
        """
        try:
            with open("/tmp/hello.txt.gz", "rb") as fh:
                resp.append_header("Content-Disposition", "attachment; filename=hello.txt.gz")
                resp.content_type = "application/gzip"
                resp.content_encoding = "gzip"
                resp.data = fh.read()
        except FileNotFoundError:
            resp.status = HTTP("404")
        except Exception as e:
            resp.status = HTTP("500")
            resp.media = {"error": str(e)}


class Binary(Resource):
    """Binary resource."""

    __routes__ = {
        "/bin/{filename}": {},
    }

    def on_get(self, _req, resp, filename):
        """
        Send contact message.

        :param str filename:    [in=path] Filename
        :response 200 binary:   All good
        :return binary:         Return data
        """
        path = f"/tmp/{filename}"
        try:
            with open(path, "rb") as fh:
                resp.stream = fh
                resp.content_type = "application/gzip"
                resp.content_encoding = "gzip"
                resp.content_length = os.path.getsize(path)
        except FileNotFoundError:
            resp.status = HTTP("404")
        except Exception as e:
            resp.status = HTTP("500")
            resp.media = {"error": str(e)}
