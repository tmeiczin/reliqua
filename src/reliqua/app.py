"""
Reliqua Framework.

Copyright 2016-2024.
"""

import configparser

from gunicorn.app.base import BaseApplication

from .api import Api
from .middleware import ProcessParams


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
    except TypeError:
        pass

    return params


class Application(BaseApplication):
    """Create a standalone API application."""

    def __init__(
        self,
        bind=None,
        api_url=None,
        swagger_url=None,
        workers=None,
        worker_class="sync",
        threads=None,
        resource_path=None,
        loglevel=None,
        middleware=None,
        version=None,
        desc=None,
        title=None,
        license=None,
        license_url=None,
        contact_name=None,
        openapi_highlight=True,
        openapi_sort="alpha",
    ):
        """
        Create Application instance.

        :param str  bind:               Address and port to listen for requests [host:port]
        :param str  api_url:            URL for API used by Swagger UI (if different from bind)
        :param str  swagger_url:        URL to the Swagger UI
        :param int  workers:            Number of worker processes
        :param int  workers_class:      Type of worker processes
        :param int  threads:            Number of threads per worker process
        :param str  resource_path:      Path to the API resource modules
        :param str  loglevel:           Log level (debug, error, info, critical)
        :param list middleware:         Middleware
        :param str  version:            Application version
        :param str  desc:               Application description
        :param str  title:              Application title
        :param str license:             API license
        :param str license_url:         API License URL
        :param str contact_name:        API Contact name
        :param bool openapi_highlight:  Enable OpenAPI syntax highlighting
        :param str openapi_sort:        OpenAPI endpoint/tag sort order

        :return:                        Application instance
        """
        middleware = middleware or []

        options = {
            "bind": "127.0.0.1:8000",
            "workers": 5,
            "api_url": None,
            "resource_path": "resource",
            "loglevel": "critical",
        }

        api_url = api_url or options["api_url"]
        resource_path = resource_path or options["resource_path"]

        self.gunicorn_options = {
            "bind": bind or options["bind"],
            "workers": workers or options["workers"],
            "loglevel": loglevel or options["loglevel"],
            "accesslog": "-",
            "errorlog": "-",
            "worker_class": worker_class,
        }

        # If a number of threads was specified, add that to the options.
        if threads:
            self.gunicorn_options["threads"] = threads
            self.gunicorn_options["worker_class"] = "gthread"

        middleware.append(ProcessParams())

        # trim slashes from proxy URL if specified; otherwise set default proxy url
        api_url = api_url.rstrip("/") if api_url else f"http://{bind}"
        self.application = Api(
            url=api_url,
            swagger_url=swagger_url,
            resource_path=resource_path,
            middleware=middleware,
            version=version,
            desc=desc,
            title=title,
            license=license,
            license_url=license_url,
            contact_name=contact_name,
            openapi_highlight=openapi_highlight,
            openapi_sort=openapi_sort,
        )

        super().__init__()

    def init(self, parser, opts, args):
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
