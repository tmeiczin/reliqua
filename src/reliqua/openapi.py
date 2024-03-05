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
        example=None,
    ):
        self.name = name
        self.location = location
        self.required = required
        self.default = default
        self.enum = enum
        self.description = description
        self.explode = explode
        self.format = format
        self.min = min
        self.max = max
        self.example = example
        self._datatype = datatype

    @property
    def datatype(self):
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
        return str(self.__dict__)

    @property
    def schema(self):
        _schema = {"type": self.datatype}
        # _schema = {"type": self.datatype, "format": self.format or self.datatype}
        if self.items_type:
            _schema["items"] = {"type": self.items_type}
        for x in ["enum", "min", "max", "default", "example"]:
            if value := getattr(self, x):
                _schema[x] = value

        if self.in_request_body():
            _schema["description"] = self.description

        return _schema

    def in_request_body(self):
        if self.location == "body":
            return True

        return False

    def request_body(self):
        return {self.name: self.schema}

    def parameter(self):
        return {
            "name": self.name,
            "in": self.location,
            "description": self.description,
            "required": self.required,
            "schema": self.schema,
        }

    def dict(self):
        if self.in_request_body():
            return self.request_body()

        return self.parameter()


class Response:
    def __init__(self, code=None, description=None, content=None):
        self.code = code
        self.description = description
        self.content = content

    def json(self):
        return {
            self.content: {
                "schema": {
                    "type": "array",
                    "items": [],
                }
            }
        }

    def __repr__(self):
        return str(self.__dict__)

    def dict(self):
        return {"description": self.description, "content": self.json()}


class Operation:
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
        **kwargs,
    ):
        self.operation = operation
        self.summary = summary
        self.description = description
        self.operation_id = operation_id
        self.tags = tags or []
        self.callbacks = callbacks or {}
        self.parameters = [Parameter(**x) for x in parameters or []]
        self.responses = [Response(**x) for x in responses or []]
        self.return_type = return_type
        self.accepts = accepts or "*/*"

    def binary_body(self):
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

    def json_body(self):
        accepts = CONTENT_MAP.get(self.accepts)
        return {
            "description": self.description,
            "content": {accepts: {"schema": [x.dict() for x in self.parameters if x.in_request_body()]}},
        }

    def request_body(self):
        if self.accepts == "binary":
            return self.binary_body()

        return self.json_body()

    def dict(self):
        return {
            self.operation: {
                "tags": self.tags,
                "summary": self.summary,
                "description": self.description,
                "operationId": self.operation_id,
                "parameters": [x.dict() for x in self.parameters if not x.in_request_body()],
                "responses": {x.code: x.dict() for x in self.responses},
                "requestBody": self.request_body(),
            }
        }


class ResourceSchema:
    def __init__(self, resource, parser=None):
        self.resource = resource
        self.routes = resource.__routes__
        self.name = resource.__class__.__name__.capitalize()
        self.tags = getattr(resource, "__tags__", [self.name.lower()])
        self.security = {verb.lower(): auth for verb, auth in getattr(resource, "__auth__", {}).items()}
        self.parser = parser() if parser else None
        self.paths = {}

    def methods(self):
        _methods = []
        for verb in verbs:
            method = getattr(self.resource, f"on_{verb}", None)
            if not method or not method.__doc__:
                continue
            _methods.append(method)

        return _methods

    def parse(self):
        self.process_routes()

    def process_parameters(self, operation):
        for parameter in operation["parameters"]:
            enum = parameter.get("enum")
            parameter["enum"] = getattr(self.resource, enum) if enum else []

        return operation

    def process_routes(self):
        for route, values in self.routes.items():
            operations = values.get("operations")
            self.process_route(route, operations=operations)

    def process_route(self, route, operations=None):
        operations = operations or verbs
        self.paths[route] = {}
        paths = self.resource.__data__[route]

        # for each resource path add the path to openapi
        for _, v in paths.items():
            data = self.process_parameters(v)
            operation = Operation(tags=self.tags, **data)
            self.paths[route].update(operation.dict())


class Info:
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
        self.title = title
        self.summary = summary
        self.description = description
        self.terms = terms
        self.contact = contact.dict()
        self.license = license.dict()
        self.version = version

    def __repr__(self):
        return str(self.__dict__)

    def dict(self):
        return self.__dict__


class License:
    def __init__(self, name=None, url=None):
        self.name = name or ""
        self.url = url or ""

    def dict(self):
        return self.__dict__


class Contact:
    """API Contact information."""

    def __init__(self, name=None, url=None, email=None):
        self.name = name
        self.url = url
        self.email = email

    def __repr__(self):
        return str(self.__dict__)

    def dict(self):
        return self.__dict__


class OpenApi:
    def __init__(
        self,
        title=None,
        description=None,
        summary=None,
        version=None,
        email=None,
        terms=None,
        license=None,
        license_url=None,
        contact_name=None,
        contact_url=None,
        contact_email=None,
        parser=None,
    ):
        self.openapi = "3.0.0"
        self.title = title or "<title>"
        self.description = description or "<description>"
        self.version = version or "0.0.0"
        self.email = email or ""
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
        self.components = {
            "securitySchemes": {},
        }
        self.parser = parser

    def process_resources(self, resources):
        for resource in resources:
            resource = ResourceSchema(resource)
            resource.parse()
            self.paths.update(resource.paths)

    def schema(self):
        return {
            "openapi": self.openapi,
            "info": self.info.dict(),
            "paths": self.paths,
            "components": self.components,
        }
