"""
Reliqua framework.

Copyright 2016-2024.
"""

from reliqua.resources.base import Resource

from .status_codes import HTTP


def index(spec, server, sort="alpha", highlight="true"):
    """
    Return the Swagger index HTML.

    This returns the Swagger index HTML contents.

    :param str spec:       URL to the OpenAPI spec
    :param str server:     URL to the server hosting Swagger UI assets
    :param str sort:       Sort order for operations and tags
    :param str highlight:  Enable syntax highlighting
    :return str:           HTML content for Swagger UI
    """
    highlight = "true" if highlight else "false"

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
            layout: "StandaloneLayout",
            syntaxHighlight: {highlight},
            operationsSorter : "{sort}",
            tagsSorter: "{sort}"
          }});
      </script>
    </html>
    """


class Swagger(Resource):
    """Class to serve the static Swagger files."""

    no_auth = True

    def __init__(self, url, openapi_url, sort="alpha", highlight=True):
        """
        Create a Swagger instance.

        :param str url:            URL to Swagger instance
        :param str openapi_url:    URL to OpenAPI spec
        :param str sort:           Tag/Endpoint sort order
        :param bool highlight:     Syntax highlighting
        """
        super().__init__()
        self.url = url
        self.openapi_url = openapi_url
        self.highlight = highlight
        self.sort = sort

    def on_get(self, _req, resp):
        """
        Return the static Swagger file.

        :param Request _req:       Request object
        :param Response resp:      Response object
        """
        resp.status = HTTP(200)
        resp.content_type = "text/html"
        resp.text = index(self.openapi_url, self.url, sort=self.sort, highlight=self.highlight)
