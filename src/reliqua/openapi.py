"""
Reliqua Framework.

Copyright 2016-2024.
"""

import re


def camelcase(string):
    """
    Convert underscore names to camel case.

    :param str string:        String to convert
    :return str:              Camel case string
    """
    return "".join(word.title() if i else word for i, word in enumerate(string.split("_")))


CONTENT_MAP = {
    "binary": "application/octet-stream",
    "json": "application/json",
    "yaml": "application/yaml",
    "xml": "application/xml",
    "html": "text/html; charset=utf-8",
    "text": "text/plain; charset=utf-8",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "form": "multipart/form-data",
    "*/*": "*/*",
}


TYPE_MAP = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "json": "object",
    "object": "object",
    "list": "array",
    "dict": "object",
}

DEFAULT_RESPONSE = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "examples": [
                "example message",
            ],
        },
    },
}

verbs = ["get", "patch", "put", "post", "delete"]


class Parameter:
    """
    OpenAPI Parameter class.

    This class represents an OpenAPI parameter.
    """

    def __init__(
        self,
        name=None,
        datatype=None,
        location=None,
        required=None,
        default=None,
        enum=None,
        description=None,
        explode=None,
        format=None,
        min=None,
        max=None,
        examples=None,
    ):
        """
        Create Parameter instance.

        Creates a parameter object.

        :param str name:        Name
        :param str datatype:    Parameter type
        :param str location:    Where parameter is located
        :param bool required:   Required parameter
        :param bool default:    Default value
        :param str enum:        Variable name of the enums
        :param str description: Parameter description
        :param bool explode:    Whether arrays and objects should generate separate parameters
        :param str format:      Parameter format type
        :param int min:         Min value
        :param int max:         Max value
        :param str examples:    Example value
        """
        self.name = name
        self.location = location or "query"
        self.required = required
        self.default = default
        self.enum = enum
        self.description = description
        self.explode = explode
        self.format = format
        self.min = min
        self.max = max
        self.examples = examples
        self._datatype = datatype

        # path parameters are always required
        if self.location == "path":
            self.required = True

        print(f"Parameter: {self.name} {self.location}")

    @property
    def datatype(self):
        """Return the parameter datatype."""
        value = self._datatype
        a, _, b = value.partition("|")

        # handle defined list type ex: list[str]
        if re.search(r"list\[(\w+)]", a):
            a = "list"

        return f"{TYPE_MAP[a]}|{TYPE_MAP[b]}" if b else f"{TYPE_MAP[a]}"

    @property
    def items_type(self):
        """
        Return a list item type.

        Return the list type when a parameter type is
        of the form list[type], such as list[int]

        :return str:     The list item type
        """
        if not self._datatype:
            return None

        if m := re.search(r"(?:list|array)\[(\w+)\]", self._datatype):
            return TYPE_MAP[m.group(1)]

        return None

    def __repr__(self):
        """Return object representation."""
        return str(self.__dict__)

    @property
    def schema(self):
        """Return parameter schema."""
        _schema = {"type": self.datatype}
        if self.items_type:
            _schema["items"] = {"type": self.items_type}
        for x in ["enum", "min", "max", "default", "examples"]:
            if value := getattr(self, x):
                _schema[x] = value

        if self.in_request_body():
            _schema["description"] = self.description
            _schema["required"] = self.required

        return _schema

    def in_request_body(self):
        """
        Return if parameter is in request body.

        Returns `True` if parameter location is in the request body.

        :return bool:     True if in request body
        """
        if self.location in ["body", "form"]:
            return True

        return False

    def request_body(self):
        """
        Return request body.

        Returns the parameter request body schema.

        :return dict:      Request body
        """
        return self.schema

    def parameter(self):
        """
        Return parameter schema.

        Return the OpenAPI parameter schema.

        :return dict:     Parameter schema

        :return _type_: _description_
        """
        return {
            "name": self.name,
            "in": self.location,
            "description": self.description,
            "schema": self.schema,
            "required": self.required,
        }

    def dict(self):
        """
        Return the parameter dict.

        Returns the parameter dict for the correct parameter type.

        :return dict:     Parameter dict
        """
        if self.in_request_body():
            return self.request_body()

        return self.parameter()


class Response:
    """Response class."""

    def __init__(self, code=None, description=None, content=None, schema=None):
        """
        Create response instance.

        :param str code:          HTTP response code
        :param str description:   Description
        :param str content:       Content type
        :param dict schema:       Schema dictionary
        :return:
        """
        self.code = code
        self.description = description
        self.content = content or "application/json"
        self.schema = schema if schema else "default_response"

    def __repr__(self):
        """Return a printable representational string."""
        return str(self.__dict__)

    def dict(self):
        """Return dict of data."""
        return {
            "description": self.description,
            "content": {self.content: {"schema": {"$ref": f"#/components/schemas/{self.schema}"}}},
        }


class Operation:
    """Operation Class."""

    def __init__(
        self,
        operation=None,
        summary=None,
        description=None,
        operation_id=None,
        parameters=None,
        tags=None,
        responses=None,
        callbacks=None,
        return_type=None,
        accepts=None,
        **_kwargs,
    ):
        """
        Create operation instance.

        :param str operation:     HTTP operation
        :param str summary:       Summary
        :param str description:   Description
        :param str operation_id:  Operation ID
        :param list parameters:   List of parameter dicts
        :param list tags:         List of tags
        :param list responses:    List of response dicts
        :param list callbacks:    List of callbacks
        :param str return_type:   Return content type
        :param str accepts:       Accepts type
        :return:
        """
        self.operation = operation
        self.summary = summary
        self.description = description
        self.operation_id = operation_id
        self.tags = tags or []
        self.callbacks = callbacks or {}
        self.parameters = [Parameter(**x) for x in parameters or []]
        self.responses = [Response(**x) for x in responses or []]
        self.return_type = return_type
        self._accepts = accepts
        self.request_body_parameters = {x.name: x.dict() for x in self.parameters if x.in_request_body()}

    @property
    def accepts(self):
        """Return accepts type."""
        if self._accepts:
            return self._accepts
        if self.has_form():
            return "form"

        return "*/*"

    def binary_body(self):
        """Return binary body."""
        accepts = CONTENT_MAP.get(self.accepts)
        return {
            "content": {
                accepts: {
                    "schema": {
                        "type": "string",
                        "format": "binary",
                    }
                }
            }
        }

    def has_form(self):
        """
        Return whether operation has form data.

        Return `True` if the operation has form data parameters.

        :return bool:     True if has form data
        """
        return [x for x in self.parameters if x.location == "form"] != []

    def body(self):
        """Return request body."""
        accepts = CONTENT_MAP.get(self.accepts)
        required = [k for k, v in self.request_body_parameters.items() if v.get("required") is True]
        return {
            "description": self.description,
            "content": {
                accepts: {
                    "schema": {"type": "object", "required": required, "properties": self.request_body_parameters}
                }
            },
        }

    def request_body(self):
        """Return request body."""
        if self.accepts in ["binary"]:
            return self.binary_body()

        return self.body()

    def dict(self):
        """Return dict of data."""
        operation = {
            "tags": self.tags,
            "summary": self.summary,
            "description": self.description,
            "operationId": self.operation_id,
            "parameters": [x.dict() for x in self.parameters if not x.in_request_body()],
            "responses": {x.code: x.dict() for x in self.responses},
        }
        if self.request_body_parameters:
            operation["requestBody"] = self.request_body()

        return {self.operation: operation}


class ResourceSchema:
    """Resource schema class."""

    def __init__(self, resource, parser=None):
        """
        Create resource instance.

        :param Resource resource:    Resource object
        :param Parser parser:        Doc string parser
        :return:
        """
        self.resource = resource
        self.routes = resource.__routes__
        self.name = resource.__class__.__name__.capitalize()
        self.tags = getattr(resource, "__tags__", [self.name.lower()])
        self.components = getattr(resource, "__components__", {})
        self.security = {verb.lower(): auth for verb, auth in getattr(resource, "__auth__", {}).items()}
        self.parser = parser() if parser else None
        self.paths = {}

    def methods(self):
        """
        Return the resource HTTP methods.

        Return the resources HTTP methods (get/put, etc)

        :return list:       List of methods
        """
        _methods = []
        for verb in verbs:
            method = getattr(self.resource, f"on_{verb}", None)
            if not method or not method.__doc__:
                continue
            _methods.append(method)

        return _methods

    def parse(self):
        """Parse the resource."""
        self.process_routes()

    def process_responses(self, operation):
        """
        Process operation responses.

        Process the responses of the operation.

        :param dict operation:     Operation dict
        :return dict:              Processed operation dict
        """
        for response in operation["responses"]:
            name = response["schema"]
            schema = getattr(self.resource, name, {})
            if schema:
                self.components[name] = schema

    def process_parameters(self, operation):
        """
        Process operation parameters.

        Process the parameters of the operation.

        :param dict operation:     Operation dict
        :return dict:              Processed operation dict
        """
        for parameter in operation["parameters"]:
            enum = parameter.get("enum")
            parameter["enum"] = getattr(self.resource, enum) if enum else []

        return operation

    def process_routes(self):
        """
        Process the resource routes.

        Process the routes defined in the resource.

        :return:
        """
        for route in self.routes.keys():
            self.process_route(route)

    def process_route(self, route):
        """
        Process resource route.

        Process the operations of the resources route.

        :param str route:         The HTTP route
        :return:
        """
        self.paths[route] = {}
        paths = self.resource.__data__[route]

        # for each resource path add the path to openapi
        for v in paths.values():
            data = self.process_parameters(v)
            operation = Operation(tags=self.tags, **data)
            self.paths[route].update(operation.dict())
            self.process_responses(v)


class Info:
    """Info class."""

    def __init__(
        self,
        title=None,
        summary=None,
        description=None,
        terms=None,
        contact=None,
        license=None,
        version=None,
    ):
        """
        Create info class instance.

        :param str title:          API Title
        :param str summary:        Summary
        :param str description:    Description
        :param str terms:          Terms
        :param Contact contact:    Contact object
        :param License license:    License object
        :param str version:        API version
        :return:
        """
        self.title = title
        self.summary = summary
        self.description = description
        self.terms = terms
        self.contact = contact.dict()
        self.license = license.dict()
        self.version = version

    def __repr__(self):
        """Return a printable representational string."""
        return str(self.__dict__)

    def dict(self):
        """Return dict of data."""
        return {
            "title": self.title,
            "summary": self.summary,
            "description": self.description,
            "termsOfService": self.terms,
            "license": self.license,
            "version": self.version,
        }


class License:
    """License class."""

    def __init__(self, name=None, url=None):
        """
        Create license instance.

        :param str name:    License name
        :param are url:     License URL
        :return:
        """
        self.name = name or ""
        self.url = url or ""

    def dict(self):
        """Return dict of data."""
        return self.__dict__


class Contact:
    """API Contact information."""

    def __init__(self, name=None, url=None, email=None):
        """
        Create contact instance.

        :param str name:    Contact name
        :param str url:     Contact URL
        :param str email:   Contact email
        :return:
        """
        self.name = name
        self.url = url
        self.email = email

    def __repr__(self):
        """Return a printable representational string."""
        return str(self.__dict__)

    def dict(self):
        """Return dict of data."""
        return self.__dict__


class OpenApi:
    """
    OpenAPI schema class.

    Class representation of the OpenAPI specification.
    """

    def __init__(
        self,
        title="",
        description="",
        summary="",
        version="",
        terms="",
        license="",
        license_url="",
        contact_name="",
        contact_url="",
        contact_email="",
        auth=None,
        parser=None,
    ):
        """
        Create an OpenAPI class.

        Creates and OpenAPI object that represents an OpenAPI
        specification document.

        :param str title:          API Title
        :param str description:    Description
        :param str summary:        Summary
        :param str version:        Version
        :param str terms:          Terms
        :param str license:        License
        :param str license_url:    URL to the License
        :param str contact_name:   Contact person
        :param str contact_url:    Software URL
        :param str contact_email:  Contact email
        :param Parser parser:      The docstring parser
        :return:
        """
        self.openapi = "3.1.0"
        self.title = title or "<title>"
        self.description = description or "<description>"
        self.version = version or "0.0.0"
        self.summary = summary or ""
        self.terms = terms or ""
        self.auth = auth or []

        contact = Contact(name=contact_name, email=contact_email, url=contact_url)
        license = License(name=license, url=license_url)
        self.info = Info(
            title=title,
            summary=summary,
            description=description,
            terms=terms,
            contact=contact,
            license=license,
            version=version,
        )
        self.paths = {}
        self.component_schemas = {
            "default_response": DEFAULT_RESPONSE,
        }
        self.parser = parser

    def process_resources(self, resources):
        """
        Generate OpenAPI data.

        Process and generate the OpenAPI data for the supplied resources.

        :param list[Resources] resources:     List of Resource objects
        :return:
        """
        for resource in resources:
            resource = ResourceSchema(resource)
            resource.parse()
            self.paths.update(resource.paths)
            self.component_schemas.update(resource.components)

    @property
    def security_schemes(self):
        """Return security schemas."""
        schema = {}
        for x in self.auth:
            schema.update(x.dict())

        return schema

    @property
    def security_names(self):
        """Return security list."""
        authenticators = [x for y in self.auth for x in y.authenticators]
        return [{x.name: []} for x in authenticators]

    @property
    def components(self):
        """Return components."""
        return {
            "securitySchemes": self.security_schemes,
            "schemas": self.component_schemas,
        }

    def schema(self):
        """Return OpenAPI Schema."""
        return {
            "openapi": self.openapi,
            "info": self.info.dict(),
            "paths": self.paths,
            "components": self.components,
            "security": self.security_names,
        }
