import falcon
import glob
import imp
import inspect
import json
import os
import re
import sys
import uuid

from six.moves import configparser
from gunicorn.app.base import BaseApplication
from falcon_cors import CORS

from . resources.base import Resource
from . middleware import ProcessParams, JsonResponse


def load_config(config_file):
    params = {}

    try:
        section = 'config'
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
            desc=None):
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

        :return:                     Application instance
        """
        middleware = middleware or []

        options = {
            'bind': '127.0.0.1:8000',
            'workers': 5,
            'proxy_api_url': None,
            'resource_path': 'resource',
            'loglevel': 'info'
        }

        proxy_api_url = proxy_api_url or options['proxy_api_url']
        resource_path = resource_path or options['resource_path'],

        self.gunicorn_options = {
            'bind': bind or options['bind'],
            'workers': workers or options['workers'],
            'loglevel': loglevel or options['loglevel']
        }

        cors = CORS(allow_all_origins=True)
        middleware.append(cors.middleware)
        middleware.append(ProcessParams())
        middleware.append(JsonResponse())

        if not proxy_api_url:
            proxy_api_url = 'http://%s' % (bind)

        self.application = Api(
            url=proxy_api_url,
            resource_path=resource_path,
            middleware=middleware,
            version=version,
            desc=desc)

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


class Api(falcon.API):
    """add auto route and documentation"""

    def __init__(
            self,
            url=None,
            resource_path=None,
            middleware=None,
            version=None,
            desc=None):
        """
        Create an API instance

        :param obj  cfg:           Gunicorn config
        :param str  url:           URL used by Swagger UI
        :param str  resource_path: Path to the resource modules
        :param list middleware:    Middleware
        :param str  version:       Application version
        :param str  desc:          Application description
        :return:                   api instance
        """
        self.doc_endpoint = '/docs'
        self.swagger_file = 'swagger.json'
        self.doc_url = url + self.doc_endpoint
        self.desc = desc
        self.version = version
        m = re.search('http[s]?://(?P<host>.*:\d+)(?P<base_path>[/]?.*)', url).groupdict()
        self.host = m['host']
        self.base_path = m['base_path']

        path = os.path.dirname(sys.modules[__name__].__file__)
        self.doc_path = path + '/swagger'

        middleware = middleware or []

        super(Api, self).__init__(
            middleware=middleware
        )

        if not resource_path:
            resource_path = self.path + '/resources'

        self.req_options.auto_parse_form_urlencoded = True
        self.resource_path = resource_path

        self._load_resources()
        self._add_routes()
        self._add_docs()

    def _load_resources(self):
        self.resources = []
        files = glob.glob('%s/*.py' % (self.resource_path))
        for f in files:
            print('loading %s' % (f))
            module_name = str(uuid.uuid3(uuid.NAMESPACE_OID, f))
            module = imp.load_source(module_name, f)
            self.resources.extend(self._get_classes(module))

        return self.resources

    def _get_classes(self, module):
        classes = []
        for n, c in inspect.getmembers(module, inspect.isclass):
            if issubclass(c, Resource) and hasattr(c, '__schema__'):
                classes.append(c)

        return classes

    def _add_routes(self):
        for resource in self.resources:
            for route in resource.__schema__.keys():
                print('adding route %s' % (route))
                self.add_route(route, resource())

    def _add_docs(self):
        swagger = Swagger(
            self.doc_url,
            self.swagger_file,
            self.doc_path
        )
        docs = Docs(
            self.resources,
            host=self.host,
            base_path=self.base_path,
            version=self.version,
            desc=self.desc
        )
        self.add_static_route(self.doc_endpoint, self.doc_path)
        self.add_route(self.doc_endpoint, swagger)
        self.add_route(self.doc_endpoint + '/' + self.swagger_file, docs)


class Swagger(object):

    def __init__(self, url, swagger_file, path):
        self.url = url
        self.swagger_file = self.url + '/' + swagger_file
        self.path = path

    def on_get(self, req, resp, filename='index.html'):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'

        with open(self.path + '/' + filename, 'r') as f:
            data = f.read()

        data = data.replace('<swagger_json_url>', self.swagger_file)
        data = data.replace('<swagger_url>', self.url)

        resp.body = data


class Docs(object):

    __schema__ = {
        'swagger': '2.0',
        'info': {
            'description': 'application description',
            'version': '0.0.0',
            'title': 'application',
        },
        'host': '127.0.0.1:8000',
        'basePath': '',
        'schemes': [
            'http',
            'https',
        ],
        'consumes': [
            'application/json',
        ],
        'produces': [
            'application/json',
        ]
    }

    def __init__(
            self,
            resources,
            desc=None,
            version=None,
            title=None,
            host=None,
            base_path=None):

        self.resources = resources

        schema = self.__schema__
        info = schema['info']
        info['description'] = desc or info['description']
        info['version'] = version or info['version']
        info['title'] = version or info['title']
        schema['host'] = host or schema['host']
        schema['basePath'] = base_path or schema['basePath']

    def on_get(self, req, resp):
        data = {'paths': {}}
        for c in self.resources:
            data['paths'].update(c.__schema__)

        data.update(self.__schema__)
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(data)
