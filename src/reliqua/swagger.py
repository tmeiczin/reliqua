"""
Reliqua framework.

Copyright 2016-2024.
"""

from .status_codes import HTTP


class Swagger:
    """Class to server the static swagger files."""

    def __init__(self, url, swagger_file, path):
        """
        Create a Swagger instance.

        :param str url:            Base url to server the Swagger file
        :param str swagger_file:   The swagger index filepath
        :param str path:           Path to swagger files
        :return:                   None
        """
        self.url = url
        self.swagger_file = self.url + "/" + swagger_file
        self.path = path

    def on_get(self, _req, resp, filename="index.html"):
        """
        Return the static swagger file.

        :param Request request:     Request object
        :param Response response:   Response object
        :param str filename:        Filename contents to return
        :return text:               File contents
        """
        resp.status = HTTP(200)
        resp.content_type = "text/html"

        with open(self.path + "/" + filename, "r", encoding="UTF-8") as fh:
            data = fh.read()

        data = data.replace("<swagger_json_url>", self.swagger_file)
        data = data.replace("<swagger_url>", self.url)

        resp.text = data
