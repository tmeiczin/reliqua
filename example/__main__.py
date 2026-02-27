"""
Reliqua Example Application.

Demonstrates application setup with:
- Multiple authentication backends (Basic + Cookie) via MultiAuthentication
- Per-resource authorization via AccessResource (deny-by-default)
- CLI argument parsing with config file fallback
- Custom resource attributes and app config passthrough
- OpenAPI metadata and server configuration
- Gunicorn worker configuration

Copyright 2016-2024.
"""

import argparse
import os

from reliqua import Application, load_config
from reliqua.auth import (
    AccessResource,
    AuthenticationContext,
    AuthMiddleware,
    BasicAuthentication,
    CookieAuthentication,
)

# ---------------------------------------------------------------------------
# Authentication callbacks
# ---------------------------------------------------------------------------
# Each callback receives credentials and returns an AuthenticationContext
# on success or None on failure. The context carries identity and role info
# that the authorization layer uses for access decisions.
# ---------------------------------------------------------------------------


def validate_basic_credentials(username, _password):
    """Validate HTTP Basic credentials.

    BasicAuthentication calls this with (username, password) extracted from
    the Authorization header. Return an AuthenticationContext on success.

    Demonstrates:
        - Returning different roles based on identity
        - Setting arbitrary attributes (user, role) on the context
    """
    known_users = {
        "admin": "admin",
        "viewer": "viewer",
    }
    role = known_users.get(username)
    if role:
        return AuthenticationContext(user=username, role=role)

    return None


def validate_cookie_api_key(api_key):
    """Validate an API key from a cookie.

    CookieAuthentication calls this with the cookie value.
    Return an AuthenticationContext on success.

    Demonstrates:
        - Token-based authentication
        - Setting name and role on the context
    """
    valid_keys = {
        "abc123": AuthenticationContext(name="api-service", role="admin"),
        "read-only": AuthenticationContext(name="reader", role="viewer"),
    }
    return valid_keys.get(api_key)


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------


def main():
    """Start the example application."""
    parser = argparse.ArgumentParser(description="Reliqua Example API Server")
    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

    parser.add_argument("--address", help="Bind address", default="127.0.0.1")
    parser.add_argument("--port", help="Bind port", type=int, default=8000)
    parser.add_argument("--ui-url", help="Public URL for OpenAPI UI (e.g., behind a proxy)")
    parser.add_argument("--docs", help="Docs URL path", default="/docs")
    parser.add_argument("--server", help="Additional OpenAPI server URLs", nargs="*")
    parser.add_argument("--resource-path", help="Path to resource modules", default=resource_path)
    parser.add_argument("--workers", help="Number of Gunicorn workers", type=int, default=2)
    parser.add_argument("--config", help="INI configuration file path", default=None)
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Optional: load config file and merge with CLI args
    # -----------------------------------------------------------------------
    # Demonstrates load_config() which reads a [config] section from an INI file.
    if args.config:
        file_config = load_config(args.config)
        for key, value in file_config.items():
            if getattr(args, key, None):
                setattr(args, key, value)

    # -----------------------------------------------------------------------
    # Authentication setup
    # -----------------------------------------------------------------------
    # Demonstrates:
    #   BasicAuthentication  — HTTP Basic (Authorization header)
    #   CookieAuthentication — API key stored in a cookie
    #   AuthMiddleware       — tries authenticators in order (first success wins)
    #   AccessResource       — reads __auth__ on each resource for role-based access;
    #                          default_mode="deny" means everything requires auth
    #                          unless the resource sets no_auth=True or __auth__
    #                          grants access via wildcard roles.
    basic_auth = BasicAuthentication(validation=validate_basic_credentials)
    cookie_auth = CookieAuthentication("api_key", validation=validate_cookie_api_key)

    auth_middleware = AuthMiddleware(
        [basic_auth, cookie_auth],
        control=AccessResource(default_mode="deny"),
    )

    # -----------------------------------------------------------------------
    # Gunicorn, info, and OpenAPI configuration
    # -----------------------------------------------------------------------
    servers = [{"url": url, "description": ""} for url in args.server] if args.server else []

    gunicorn = {
        "bind": f"{args.address}:{args.port}",
        "workers": args.workers,
        "worker_class": "gthread",
        "threads": 2,
    }

    info = {
        "title": "Reliqua Example API",
        "version": "1.0.0",
        "description": "Comprehensive example demonstrating all Reliqua features",
        "license": "MIT License",
        "license_url": "https://opensource.org/license/mit",
        "contact_name": "Terrence Meiczinger",
    }

    openapi = {
        "highlight": True,
        "sort": "alpha",
        "ui_url": args.ui_url,
        "docs": args.docs,
        "servers": servers,
    }

    # -----------------------------------------------------------------------
    # Create and run the application
    # -----------------------------------------------------------------------
    # Demonstrates:
    #   resource_path       — auto-discovers all Resource subclasses in this directory
    #   middleware           — auth middleware is applied to every request
    #   config              — accessible in resources via self.app_config
    #   resource_attributes — every resource gets self.version set automatically
    app = Application(
        resource_path=args.resource_path,
        middleware=[auth_middleware],
        config=vars(args),
        resource_attributes={"version": "1.0.0"},
        info=info,
        openapi=openapi,
        gunicorn=gunicorn,
    )
    app.run()


if __name__ == "__main__":
    main()
