"""
MIT License.

Copyright (c) 2017 Terrence Meiczinger

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import glob
import importlib
import inspect
import os
import re
import sys
import uuid

import falcon
from falcon_cors import CORS

from .auth import AuthMiddleware
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
        resource_path=None,
        middleware=None,
        config=None,
        resource_attributes=None,
        info=None,
        openapi=None,
        **_kwargs,
    ):
        """
        Create an API instance.

        :param str resource_path:             Path to the resource modules
        :param list middleware:               Middleware
        :param dict config:                   API configuration parameters
        :param dict resource_attributes:      Parameters added as resource attributes
        :param dict info:                     Application information
        :param dict openapi:                  OpenAPI configuration options

        :return:                               API instance
        """
        info = info or {}
        openapi = openapi or {}

        openapi_path = openapi["path"]
        self.url = openapi["ui_url"]
        self.servers = openapi["servers"]

        self.openapi = openapi
        self.info = info

        self.openapi["spec"] = f"{openapi_path}/openapi.json"
        self.openapi["static"] = f"{openapi_path}/static"
        self.resources = []
        self.auth = [x for x in middleware if isinstance(x, AuthMiddleware)]
        self.config = config or {}
        self.resource_attributes = resource_attributes or {}

        path = os.path.dirname(sys.modules[__name__].__file__)
        self.openapi["file_path"] = f"{path}/swagger"
        self.openapi["spec_url"] = f"{self.url}{self.openapi['spec']}"
        self.openapi["static_url"] = f"{self.url}{self.openapi['static']}"

        middleware = middleware or []
        cors = CORS(allow_all_origins=True, allow_all_methods=True, allow_all_headers=True)
        middleware.append(cors.middleware)

        super().__init__(middleware=middleware)

        if not resource_path:
            resource_path = path + "/resources"

        self.resource_path = resource_path

        self._add_handlers()
        self._load_resources()
        self._parse_docstrings()
        self._add_routes()
        self._add_docs()

    def _add_handlers(self):
        """Add custom media handlers."""
        extra_handlers = {
            "application/yaml": YAMLHandler(),
            "text/html; charset=utf-8": TextHandler(),
            "text/plain; charset=utf-8": TextHandler(),
            "application/json": JSONHandler(),
        }

        self.req_options.media_handlers.update(extra_handlers)  # pyright: ignore[reportAttributeAccessIssue]
        self.resp_options.media_handlers.update(extra_handlers)  # pyright: ignore[reportAttributeAccessIssue]

    def _load_resources(self):
        """Load resource classes from the specified resource path."""
        resources = []
        path = f"{self.resource_path}/*.py"
        print(f"searching {path}")
        files = glob.glob(path)

        for file in files:
            print(f"loading {file}")
            classes = self._get_classes(file)
            resources.extend(classes)

        # Add config to resource
        self.resources = [x(app_config=self.config, **self.resource_attributes) for x in resources]

    def _is_route_method(self, name, suffix):
        """Check if a method name is a route method."""
        if not name.startswith("on_"):
            return None

        if suffix:
            return name.endswith(suffix)

        return re.search(r"^on_([a-z]+)$", name)

    def _parse_methods(self, resource, route, methods):
        """Parse methods of a resource for a given route."""
        parser = SphinxParser()
        for name in methods:
            operation_id = f"{resource.__class__.__name__}.{name}"
            action = re.search(r"on_(delete|get|patch|post|put)", name).group(1)
            method = getattr(resource, name)
            resource.__data__[route][action] = parser.parse(method, operation_id=operation_id)

    def _parse_resource(self, resource):
        """Parse a resource to extract routes and methods."""
        for route, data in resource.__routes__.items():
            resource.__data__[route] = {}
            suffix = data.get("suffix", None)
            methods = [x for x in dir(resource) if self._is_route_method(x, suffix)]
            self._parse_methods(resource, route, methods)

    def _parse_docstrings(self):
        """Parse docstrings of all resources."""
        for resource in self.resources:
            resource.__data__ = {}
            self._parse_resource(resource)

    def _get_classes(self, filename):
        """Get resource classes from a file."""
        classes = []
        module_name = str(uuid.uuid3(uuid.NAMESPACE_OID, filename))
        spec = importlib.util.spec_from_file_location(module_name, filename)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except (ImportError, FileNotFoundError, SyntaxError, TypeError, AttributeError) as e:
            print(f"Error loading module {module_name}: {e}")
            return classes

        for _, c in inspect.getmembers(module, inspect.isclass):
            if issubclass(c, Resource) and hasattr(c, "__routes__"):
                classes.append(c)

        return classes

    def _add_routes(self):
        """Add routes for all resources."""
        for resource in self.resources:
            routes = resource.__routes__
            for route, kwargs in routes.items():
                self.add_route(route, resource, **kwargs)

    def _add_docs(self):
        """Add Swagger and OpenAPI documentation routes."""
        swagger = Swagger(
            self.openapi["static_url"],
            self.openapi["spec_url"],
            sort=self.openapi["sort"],
            highlight=self.openapi["highlight"],
        )
        openapi = OpenApi(**self.info, auth=self.auth, servers=self.servers)
        openapi.process_resources(self.resources)
        schema = openapi.schema()
        print(f"adding static route {self.openapi['docs']} {self.openapi['file_path']}")
        self.add_static_route(self.openapi["static"], self.openapi["file_path"])
        self.add_route(self.openapi["docs"], swagger)
        print(f"adding openapi file {self.openapi['spec']}")
        self.add_route(self.openapi["spec"], Docs(schema))
