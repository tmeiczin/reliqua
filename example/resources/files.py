"""
Files resource — demonstrates binary and streaming responses.

Features shown:
- Binary response content type (:return binary:)
- Gzip response content type (:return gzip:)
- Streaming responses via resp.data and resp.stream
- Content-Disposition headers for file downloads
- Path parameter for dynamic filenames
- Text/plain response content type (:return text:)
- YAML response content type (:return yaml:)

Copyright 2016-2024.
"""

import yaml

from reliqua.resources.base import Resource


class Download(Resource):
    """File download endpoint.

    Demonstrates:
    - Binary/gzip streaming response using resp.data
    - Setting Content-Disposition for file download
    - :return gzip: content type declaration
    """

    __routes__ = {"/files/download": {}}

    __tags__ = ["files"]

    __auth__ = {
        "GET": ["admin", "viewer"],
    }

    def on_get(self, _req, resp):
        """
        Download a sample file.

        Returns a gzip-compressed file as a download attachment.
        In a real application this would read from disk or object storage.

        :response 200:          File data returned
        :return gzip:
        """
        # Simulate gzip file content
        content = b"This is a sample file for download demonstration."
        resp.data = content
        resp.content_type = "application/gzip"
        resp.append_header("Content-Disposition", "attachment; filename=sample.gz")


class TextFile(Resource):
    """Plain text response endpoint.

    Demonstrates:
    - :return text: content type (text/plain)
    - Direct resp.text for text responses
    """

    __routes__ = {"/files/text": {}}

    __tags__ = ["files"]

    __auth__ = {
        "GET": ["admin", "viewer"],
    }

    def on_get(self, _req, resp):
        """
        Get a plain text response.

        Returns data as plain text instead of JSON.

        :response 200:          Text content returned
        :return text:
        """
        resp.content_type = "text/plain; charset=utf-8"
        resp.text = "Hello from the Reliqua example application!\nThis is plain text."


class YamlFile(Resource):
    """YAML response endpoint.

    Demonstrates:
    - :return yaml: content type (application/yaml)
    - YAML media handler serialization
    """

    __routes__ = {"/files/yaml": {}}

    __tags__ = ["files"]

    __auth__ = {
        "GET": ["admin", "viewer"],
    }

    version = None

    def on_get(self, _req, resp):
        """
        Get a YAML response.

        Returns data serialized as YAML using the built-in YAMLHandler.

        :response 200:          YAML content returned
        :return yaml:
        """
        data = {
            "application": "reliqua-example",
            "features": ["routing", "auth", "openapi", "yaml"],
            "version": self.version,
        }
        resp.content_type = "application/yaml"
        resp.data = yaml.dump(data, default_flow_style=False).encode("utf-8")
