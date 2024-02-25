import falcon
import glob
import imp
import inspect
import os
import sys
import uuid

from falcon_cors import CORS

from .docs import Docs
from .openapi import OpenApi
from .sphinx_parser import SphinxParser
from .resources.base import Resource
from .swagger import Swagger
from .media_handlers import JSONHandler, TextHandler, YAMLHandler


class Api(falcon.App):
    """add auto route and documentation"""

    def __init__(
        self,
        url=None,
        resource_path=None,
        middleware=None,
        version=None,
        desc=None,
        title=None,
    ):
        """
        Create an API instance

        :param obj  cfg:           Gunicorn config
        :param str  url:           URL used by Swagger UI
        :param str  resource_path: Path to the resource modules
        :param list middleware:    Middleware
        :param str  version:       Application version
        :param str  desc:          Application description
        :param str  title:         Application title

        :return:                   api instance
        """
        self.doc_endpoint = "/docs"
        self.swagger_file = "swagger.json"
        self.url = url
        self.doc_url = url + self.doc_endpoint
        self.desc = desc
        self.title = title
        self.version = version
        self.resources = []

        path = os.path.dirname(sys.modules[__name__].__file__)
        self.doc_path = path + "/swagger"

        middleware = middleware or []
        cors = CORS(
            allow_all_origins=True, allow_all_methods=True, allow_all_headers=True
        )
        middleware.append(cors.middleware)

        super(Api, self).__init__(middleware=middleware)

        if not resource_path:
            resource_path = self.path + "/resources"

        self.req_options.auto_parse_form_urlencoded = True
        self.resource_path = resource_path

        self._add_handlers()
        self._load_resources()
        self._parse_docstrings()
        self._add_routes()
        self._add_docs()

    def _add_handlers(self):
        extra_handlers = {
            "application/yaml": YAMLHandler(),
            "text/html; charset=utf-8": TextHandler(),
            "text/plain; charset=utf-8": TextHandler(),
            "application/json": JSONHandler(),
        }

        self.req_options.media_handlers.update(extra_handlers)
        self.resp_options.media_handlers.update(extra_handlers)

    def _load_resources(self):
        resources = []
        path = f"{self.resource_path}/*.py"
        path = "%s/*.py" % (self.resource_path)
        print(f"searching {path}")
        files = glob.glob(path)

        for file in files:
            print(f"loading {file}")
            classes = self._get_classes(file)
            resources.extend(classes)

        self.resources = [x() for x in resources]

    def _parse_docstrings(self):
        parser = SphinxParser()
        for resource in self.resources:
            resource.__data__ = {}
            methods = [x for x in dir(resource) if x.startswith("on_")]
            for name in methods:
                operation_id = f"{resource.__class__.__name__}.{name}"
                action = name.replace("on_", "")
                method = getattr(resource, name)
                resource.__data__[action] = parser.parse(
                    method, operation_id=operation_id
                )

    def _get_classes(self, filename):
        classes = []
        module_name = str(uuid.uuid3(uuid.NAMESPACE_OID, filename))
        module = imp.load_source(module_name, filename)

        for n, c in inspect.getmembers(module, inspect.isclass):
            if issubclass(c, Resource) and hasattr(c, "__routes__"):
                classes.append(c)

        return classes

    def _add_routes(self):
        for resource in self.resources:
            routes = getattr(resource, "__routes__")
            for route, kwargs in routes.items():
                print(f"adding route {route} {kwargs}")
                self.add_route(route, resource, **kwargs)

    def _add_docs(self):
        swagger = Swagger(self.doc_url, self.swagger_file, self.doc_path)
        openapi = OpenApi(
            title=self.title,
            description=self.desc,
            version=self.version,
            license="Apache 2.0",
            license_url="http://foo.com",
            contact_name="Terrence Meiczinger",
        )
        openapi.process_resources(self.resources)
        schema = openapi.schema()
        print(f"adding docs {self.doc_endpoint} {self.doc_path}")
        self.add_static_route(self.doc_endpoint, self.doc_path)
        self.add_route(self.doc_endpoint, swagger)
        self.add_route(self.doc_endpoint + "/" + self.swagger_file, Docs(schema))
