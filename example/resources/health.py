"""
Health resource — demonstrates a minimal public status endpoint.

Features shown:
- no_auth = True for unauthenticated public access
- Accessing resource_attributes (self.version) set in Application constructor
- Accessing app_config (self.app_config) passed from Application config
- status_codes helper for HTTP status strings
- Simple JSON response with no parameters

Copyright 2016-2024.
"""

from reliqua import status_codes as status
from reliqua.resources.base import Resource


class Health(Resource):
    """Health check endpoint.

    Demonstrates:
    - Minimal resource with no parameters
    - no_auth = True: publicly accessible without credentials
    - self.version: a custom resource_attribute set in Application()
    - self.app_config: the config dict passed to Application()
    - status_codes.http() for building status strings
    """

    __routes__ = {"/health": {}}

    __tags__ = ["health"]

    # Public — no authentication required
    no_auth = True
    version = None  # This will be set from Application constructor

    def on_get(self, _req, resp):
        """
        Health check.

        Returns the current health status of the API. This endpoint
        requires no authentication and accepts no parameters.

        :response 200:      Service is healthy

        :return json:
        """
        resp.media = {
            "status": "ok",
            "version": self.version,
            "status_code": status.http(200),
        }
