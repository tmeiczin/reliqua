import falcon
import glob
import imp
import inspect
import json
import os
import sys
import uuid

from gunicorn.app.base import BaseApplication
from falcon_cors import CORS

from resources.base import Resource


class Application(BaseApplication):
    """create a standalone application"""

    def __init__(
            self,
            app=None,
            address='127.0.0.1',
            port=8000,
            host=None,
            base_path='',
            workers=1,
            resource_path=None,
            middleware=None):
        """
        Create a standalone API application

        :param App app:           An optional app instance
        :param str address:       Bind address to listen for requests
        :param int port:          Bind port to listen on
        :param str host:          External hostname/ip for Swagger UI
        :param str base_path:     External API url for Swaager UI
        :param int workers:       Number of worker threads
        :param str resource_path: Path to the API resource modules
        :param list middleware:   Middleware
        :return:                  Application instance
        """
        middleware = middleware or []
        self.options = {
            'bind': '%s:%s' % (address, port),
            'workers': workers
        }

        cors = CORS(allow_all_origins=True)
        middleware.append(cors.middleware)
        self.application = app or Api(
            host='%s:%s' % (host, port),
            base_path=base_path,
            resource_path=resource_path,
            middleware=middleware)
        super(Application, self).__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class Api(falcon.API):
    """add auto route and documentation"""

    def __init__(
            self,
            cfg=None,
            host=None,
            resource_path=None,
            base_path='',
            middleware=None):
        """
        Create an API instance

        :param obj cfg:           Gunicorn config
        :param str host:          External hostname/ip for Swagger UI
        :param str resource_path: Path to the resource modules
        :param str base_path:     External API url for Swaager UI
        :param list middleware:   Middleware
        :return:                  api instance
        """
        self.host = host
        self.base_path = base_path
        self.url = 'http://' + self.host + self.base_path

        self.path = os.path.dirname(sys.modules[__name__].__file__)
        self.doc_path = self.path + '/swagger'

        middleware = middleware or []

        super(Api, self).__init__(
            middleware=middleware
        )

        if not resource_path:
            resource_path = self.path + '/resources'

        self.req_options.auto_parse_form_urlencoded = True
        self.resource_path = resource_path
        self.cfg = cfg

        self._load_resources()
        self._add_routes()
        self._add_docs()

    def _load_resources(self):
        self.resources = []
        files = glob.glob(self.resource_path + '/*.py')
        for f in files:
            print 'loading %s' % (f)
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
                print 'adding route %s' % (route)
                self.add_route(route, resource())

    def _add_docs(self, path='/docs/swagger.json'):
        swagger = Swagger(
            '%s/docs/swagger.json' % (self.url,),
            path=self.doc_path,
        )
        docs = Docs(
            self.resources,
            host=self.host,
            base_path=self.base_path
        )
        static = SwaggerStatic(
            self.doc_path
        )
        self.add_route('/docs', swagger)
        self.add_route('/docs/{filename}', static)
        self.add_route(path, docs)


class Swagger(object):

    def __init__(self, url, path=None):
        self.url = url
        self.path = path

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'

        with open(self.path + '/index.html', 'r') as f:
            data = f.read()

        resp.body = data.replace('<api_url>', self.url)


class SwaggerStatic(object):

    def __init__(self, path):
        self.path = path

    def on_get(self, req, resp, filename):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'

        if 'css' in filename:
            resp.content_type = 'text/css'

        with open(self.path + '/' + filename, 'r') as f:
            resp.body = f.read()


class Docs(object):

    __schema__ = {
        'swagger': '2.0',
        'info': {
            'description': 'application description',
            'version': '0.0.0',
            'title': 'application',
        },
        'host': '127.0.0.1',
        'basePath': '',
        'schemes': [
            'http'
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

        if desc:
            self.__schema__['info']['description'] = desc
        if version:
            self.__schema__['info']['version'] = version
        if title:
            self.__schema__['info']['title'] = title
        if host:
            self.__schema__['host'] = host
        if base_path:
            self.__schema__['basePath'] = base_path

    def on_get(self, req, resp):
        data = {'paths': {}}
        for c in self.resources:
            data['paths'].update(c.__schema__)

        data.update(self.__schema__)
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(data)
