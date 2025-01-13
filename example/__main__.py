"""
Reliqua Framework.

Copyright 2016-2024.
"""

import argparse
import os
import sys

from reliqua import Application, load_config
from reliqua.auth import (
    AccessResource,
    AuthMiddleware,
    BasicAuthentication,
    CookieAuthentication,
    AuthenticationContext,
)


def check_user(username, _password):
    """Return if user is authenticated."""
    if username == "ted":
        return AuthenticationContext(user="ted", role="admin")

    return None


def check_api_key(api_key):
    """Return if user is authenticated."""
    if api_key == "abc123":
        return AuthenticationContext(name="ted", role="admin")

    return None


def main():
    """Execute main method."""
    bind_address = "127.0.0.01"
    bind_port = 8000
    api_url = None
    workers = 2
    parser = argparse.ArgumentParser()
    resource_path = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__)) + "/resources"

    parser.add_argument(
        "--address",
        help="API bind address to listen for requests",
        default=bind_address,
    )
    parser.add_argument("--port", help="Bind port to listen for requests", default=bind_port)
    parser.add_argument("--api-url", help="API URL", default=api_url)
    parser.add_argument("--resource-path", help="Path to API resource modules", default=resource_path)
    parser.add_argument("--workers", help="Number of worker threads", default=workers)
    parser.add_argument("--config", help="Configuration file", default=None)

    basic_auth = BasicAuthentication(
        validation=check_user,
    )
    cookie_auth = CookieAuthentication(
        "api_key",
        validation=check_api_key,
    )

    auth = AuthMiddleware([basic_auth, cookie_auth], control=AccessResource(default_mode="deny"))

    args = parser.parse_args()
    middleware = [auth]
    if args.config:
        config = load_config(args.config)
        for k, v in config.items():
            if getattr(args, k, None):
                setattr(args, k, v)

    app = Application(
        bind=f"{args.address}:{args.port}",
        workers=args.workers,
        threads=2,
        worker_class="gthread",
        resource_path=args.resource_path,
        api_url=args.api_url,
        version="1.0.0",
        desc="Example API",
        title="Reliqua Example",
        loglevel="info",
        accesslog=None,
        middleware=middleware,
        license="3-Clause BSD License",
        license_url="https://opensource.org/license/bsd-3-clause",
        contact_name="Terrence Meiczinger",
        openapi_highlight=True,
        openapi_sort="alpha",
    )
    app.run()


if __name__ == "__main__":
    main()
