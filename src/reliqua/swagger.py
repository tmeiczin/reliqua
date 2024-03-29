"""
Reliqua framework.

Copyright 2016-2024.
"""

from .status_codes import HTTP


def index(spec, server):
    """
    Return the Swagger index HTML.

    This returns the Swagger index html contents.
    """
    return f"""<!-- HTML for static distribution bundle build -->
    <!DOCTYPE html>
    <html lang="en">
      <head>
      <meta charset="UTF-8">
        <title>Swagger UI</title>
        <link rel="stylesheet" type="text/css" href="{server}/swagger-ui.css" />
        <link rel="stylesheet" type="text/css" href="{server}/index.css" />
        <link rel="icon" type="image/png" href="{server}/favicon-32x32.png" sizes="32x32" />
        <link rel="icon" type="image/png" href="{server}/favicon-16x16.png" sizes="16x16" />
      </head>

      <body>
        <div id="swagger-ui"></div>
        <script src="{server}/swagger-ui-bundle.js" charset="UTF-8"> </script>
        <script src="{server}/swagger-ui-standalone-preset.js" charset="UTF-8"> </script>
      </body>

      <script>
          const ui = SwaggerUIBundle({{
            url: "{spec}",
            validatorUrl: null,
            dom_id: '#swagger-ui',
            deepLinking: true,
            queryConfigEnabled: true,
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIStandalonePreset
            ],
            plugins: [
              SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
          }});
      </script>
    </html>
    """


class Swagger:
    """Class to server the static swagger files."""

    def __init__(self, url, openapi_url):
        """
        Create a Swagger instance.

        :param str url:            URL to Swagger instance
        :param str swagger_file:   URL to Swagger file
        :return:                   None
        """
        self.url = url
        self.openapi_url = openapi_url

    def on_get(self, _req, resp):
        """
        Return the static swagger file.

        :param Request request:     Request object
        :param Response response:   Response object
        :param str filename:        Filename contents to return
        :return text:               File contents
        """
        resp.status = HTTP(200)
        resp.content_type = "text/html"
        resp.text = index(self.openapi_url, self.url)
