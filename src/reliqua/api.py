"""
Reliqua Framework.

Copyright 2016-2024.
"""

import glob
import imp
import inspect
import os
import re
import sys
import uuid

import falcon
from falcon_cors import CORS

from .docs import Docs
from .media_handlers import JSONHandler, TextHandler, YAMLHandler
from .openapi import OpenApi
from .resources.base import Resource
from .sphinx_parser import SphinxParser
from .swagger import Swagger


class Api(falcon.App):
    """Add auto route and documentation."""

    def __init__(
        self,
        url=None,
        swagger_url=None,
        resource_path=None,
        middleware=None,
        config=None,
        version=None,
        desc=None,
        title=None,
    ):
        """
        Create an API instance.

        :param str url:            API URL used by Swagger UI
        :param str swagger_url:    URL to Swagger instance
        :param str resource_path:  Path to the resource modules
        :param list middleware:    Middleware
        :param str version:        Application version
        :param str desc:           Application description
        :param str title:          Application title
        :param dict config:        API configuration parameters

        :return:                   api instance
        """
        self.doc_endpoint = "/docs"
        self.openapi_spec = "/openapi/openapi.json"
        self.openapi_static = "/openapi/static"
        self.desc = desc
        self.title = title
        self.version = version
        self.resources = []
        self.config = config or {}

        path = os.path.dirname(sys.modules[__name__].__file__)
        self.url = url
        self.swagger_path = f"{path}/swagger"
        self.openapi_server = swagger_url
        self.openapi_spec_url = f"{self.url}{self.openapi_spec}"
        self.openapi_static_url = f"{self.url}{self.openapi_static}"

        middleware = middleware or []
        cors = CORS(allow_all_origins=True, allow_all_methods=True, allow_all_headers=True)
        middleware.append(cors.middleware)

        super().__init__(middleware=middleware)

        if not resource_path:
            resource_path = path + "/resources"

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
        print(f"searching {path}")
        files = glob.glob(path)

        for file in files:
            print(f"loading {file}")
            classes = self._get_classes(file)
            resources.extend(classes)

        self.resources = [x() for x in resources]

    def _is_route_method(self, name, suffix):
        if not name.startswith("on_"):
            return None

        if suffix:
            return name.endswith(suffix)

        return re.search(r"^on_([a-z]+)$", name)

    def _parse_methods(self, resource, route, methods):
        parser = SphinxParser()
        for name in methods:
            operation_id = f"{resource.__class__.__name__}.{name}"
            action = re.search(r"on_(delete|get|patch|post|put)", name).group(1)
            method = getattr(resource, name)
            resource.__data__[route][action] = parser.parse(method, operation_id=operation_id)

    def _parse_resource(self, resource):
        for route, data in resource.__routes__.items():
            resource.__data__[route] = {}
            suffix = data.get("suffix", None)
            methods = [x for x in dir(resource) if self._is_route_method(x, suffix)]
            self._parse_methods(resource, route, methods)

    def _parse_docstrings(self):
        for resource in self.resources:
            resource.__data__ = {}
            self._parse_resource(resource)

    def _get_classes(self, filename):
        classes = []
        module_name = str(uuid.uuid3(uuid.NAMESPACE_OID, filename))
        module = imp.load_source(module_name, filename)

        for _, c in inspect.getmembers(module, inspect.isclass):
            if issubclass(c, Resource) and hasattr(c, "__routes__"):
                classes.append(c)

        return classes

    def _add_routes(self):
        for resource in self.resources:
            routes = resource.__routes__
            for route, kwargs in routes.items():
                self.add_route(route, resource, **kwargs)

    def _add_docs(self):
        swagger = Swagger(self.openapi_static_url, self.openapi_spec_url)
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
        print(f"adding static route {self.doc_endpoint} {self.swagger_path}")
        self.add_static_route(self.openapi_static, self.swagger_path)
        self.add_route(self.doc_endpoint, swagger)
        print(f"adding swagger file {self.openapi_spec}")
        self.add_route(self.openapi_spec, Docs(schema))
