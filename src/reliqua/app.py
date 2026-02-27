"""
Reliqua Framework.

Copyright 2016-2024.
"""

import configparser
import logging

from gunicorn.app.base import BaseApplication

from .api import Api
from .middleware import ProcessParams

GUNICORN_DEFAULTS = {
    "bind": "127.0.0.1:8000",  # Address and port to listen for requests [host:port]
    "workers": 1,  # Number of worker processes
    "loglevel": "critical",  # Log level (debug, error, info, critical)
    "accesslog": "-",  # Access log path ("-" for stream, None to disable)
    "errorlog": "-",  # Error log path ("-" for stream, None to disable)
    "worker_class": "gthread",  # Type of worker processes
    "timeout": 30,  # Inactive worker timeout (worker killed)
    "keepalive": 2,  # Keep alive period for a request
}

OPENAPI_DEFAULTS = {
    "ui_url": None,  # Swagger UI index URL (if different from bind, for example, behind a proxy))
    "highlight": True,  # Enable OpenAPI syntax highlighting
    "sort": "alpha",  # OpenAPI endpoint/tag sort order
    "path": "/openapi",  # OpenAPI endpoint path (JSON and static files)
    "docs": "/docs",  # Documentation endpoint
    "servers": [],  # List of target API servers (default is bind address)
}

INFO_DEFAULTS = {
    "title": "Application Title",  # Application title
    "version": "1.0.0",  # Application version
    "description": "",  # Application description
    "license": "",  # License
    "license_url": "",  # License URL
    "contact_name": "",  # Contact name
}


def update_dict(overrides, defaults):
    """
    Merge user overrides into a defaults dictionary.

    Return a new dictionary containing only keys defined in `defaults`,
    with values from `overrides` taking precedence when present.

    :param dict overrides:  User-supplied values
    :param dict defaults:   Default values (also defines valid keys)
    :return dict:           Merged dictionary
    """
    return {key: overrides.get(key, defaults[key]) for key in defaults}


def load_config(config_file):
    """
    Load configuration file.

    :param str config_file:    Configuration file
    :return dict:              Options dictionary
    """
    params = {}

    try:
        section = "config"
        config = configparser.ConfigParser()
        config.read(config_file)

        for option in config.options(section):
            params[option] = config.get(section, option)
    except (TypeError, configparser.Error) as e:
        logging.getLogger(__name__).error("Error loading config file: %s", e)

    return params


class Application(BaseApplication):
    """Create a standalone API application."""

    def __init__(
        self,
        resource_path=None,
        middleware=None,
        config=None,
        resource_attributes=None,
        info=None,
        openapi=None,
        gunicorn=None,
        cors_options=None,
    ):
        """
        Create Application instance.

        :param str resource_path:         Path to the API resource modules
        :param list middleware:           Middleware
        :param dict config:               Application resource parameters (passed to resources as config attribute)
        :param dict resource_attributes:  Parameters added as resource attributes
        :param str info:                  Application information
        :param str openapi:               OpenAPI configuration options
        :param dict gunicorn:             Gunicorn configuration options
        :param dict cors_options:         CORS configuration options for falcon-cors

        :return:                          Application instance
        """
        middleware = middleware or []
        gunicorn = gunicorn or {}
        openapi = openapi or {}
        info = info or {}

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
        )

        resource_path = resource_path or ""
        resource_attributes = resource_attributes or {}

        self.gunicorn_options = update_dict(gunicorn, GUNICORN_DEFAULTS)
        openapi = update_dict(openapi, OPENAPI_DEFAULTS)
        info = update_dict(info, INFO_DEFAULTS)

        middleware.append(ProcessParams())

        # Trim slashes from proxy URL if specified; otherwise set default proxy URL
        bind = self.gunicorn_options["bind"]
        openapi["ui_url"] = openapi["ui_url"].rstrip("/") if openapi["ui_url"] else f"http://{bind}"

        # Add default api server if none specified
        if len(openapi["servers"]) == 0:
            openapi["servers"] = [{"url": openapi["ui_url"], "description": "Default server"}]

        self.application = Api(
            resource_path=resource_path,
            middleware=middleware,
            config=config,
            resource_attributes=resource_attributes,
            openapi=openapi,
            info=info,
            cors_options=cors_options,
        )

        super().__init__()

    def init(self, _parser, _opts, _args):
        """
        Init method.

        This is not invoked, since the load_config method
        is also overridden.
        """
        return

    def load_config(self):
        """
        Load configuration.

        Default config loader. This load settings from a config file
        with a 'config' section. This method should be overloaded
        if a custom loader is required.
        """
        for key, value in self.gunicorn_options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        """
        Load the application.

        Base class.
        """
        return self.application
