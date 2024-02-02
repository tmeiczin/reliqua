import configparser
from gunicorn.app.base import BaseApplication

from .api import Api
from .middleware import ProcessParams


def load_config(config_file):
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
    """
    Create a standalone restful application
    """

    def __init__(
        self,
        bind=None,
        proxy_api_url=None,
        workers=None,
        resource_path=None,
        loglevel=None,
        middleware=None,
        version=None,
        desc=None,
        title=None,
    ):
        """
        Application init method

        :param str  bind:             Address and port to listen for requests [host:port]
        :param str  proxy_api_url:    Proxy URL for API used by Swagger UI (if different from bind)
        :param int  workers:          Number of worker threads
        :param str  resource_path:    Path to the API resource modules
        :param str  loglevel:         Log level (debug, error, info, critical)
        :param list middleware:       Middleware
        :param str  version:          Application version
        :param str  desc:             Application description
        :param str  title:            Application title

        :return:                      Application instance
        """
        middleware = middleware or []

        options = {
            "bind": "127.0.0.1:8000",
            "workers": 5,
            "proxy_api_url": None,
            "resource_path": "resource",
            "loglevel": "info",
        }

        proxy_api_url = proxy_api_url or options["proxy_api_url"]
        resource_path = (resource_path or options["resource_path"],)

        self.gunicorn_options = {
            "bind": bind or options["bind"],
            "workers": workers or options["workers"],
            "loglevel": loglevel or options["loglevel"],
        }

        middleware.append(ProcessParams())

        # trim slashes from proxy URL if specified; otherwise set default proxy url
        proxy_api_url = (
            proxy_api_url.rstrip("/") if proxy_api_url else "http://%s" % (bind)
        )

        self.application = Api(
            url=proxy_api_url,
            resource_path=resource_path,
            middleware=middleware,
            version=version,
            desc=desc,
            title=title,
        )

        super(Application, self).__init__()

    def load_config(self):
        """
        Default config loader. This load settings from a config file
        with a 'config' section. This method should be overloaded
        if a custom loader is required.
        """
        for key, value in self.gunicorn_options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
