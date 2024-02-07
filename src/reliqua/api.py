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
from .resources.base import Resource
from .swagger import Swagger


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

        self._load_resources()
        self._add_routes()
        self._add_docs()

    def _load_resources(self):
        resources = []
        path = f"{self.resource_path}/*.py"
        path = "%s/*.py" % (self.resource_path)
        print(f"searching {path}")
        files = glob.glob(path)
        for f in files:
            print(f"loading {f}")
            module_name = str(uuid.uuid3(uuid.NAMESPACE_OID, f))
            module = imp.load_source(module_name, f)
            resources.extend(self._get_classes(module))

        self.resources = [x() for x in resources if hasattr(x, "__routes__")]

    def _get_classes(self, module):
        classes = []
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
