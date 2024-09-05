"""
Reliqua Framework.

Copyright 2016-2024.
"""

import os

from reliqua.resources.base import Resource


class Gzip(Resource):
    """GZIP resource."""

    __routes__ = {
        "/gzip": {},
    }

    def on_get(self, req, resp):
        """
        Send contact message.

        :accepts json:          Accepts JSON
        :response 200 binary:       All good
        :return gzip:      Return data
        """
        fh = open("/tmp/hello.txt.gz", "rb")
        resp.append_header("Content-Disposition", "attachment; filename=hello.txt.gz")
        resp.content_type = "application/gzip"
        resp.content_encoding = "gzip"
        resp.data = fh.read()


class Binary(Resource):
    """Binary resource."""

    __routes__ = {
        "/bin/{filename}": {},
    }

    def on_get(self, req, resp, filename):
        """
        Send contact message.

        :param str filename:    [in=path] Filename
        :response 200 binary:       All good
        :return binary:         Return data
        """
        path = f"/tmp/{filename}"
        resp.stream = open(path, "rb")
        resp.content_type = "application/gzip"
        resp.content_encoding = "gzip"
        resp.content_length = os.path.getsize(path)
