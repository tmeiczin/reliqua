"""
Reliqua Framework.

Copyright 2016-2024.
"""

import json
import re

import falcon

TRANSFORMS = {
    "string": str,
    "str": str,
    "number": float,
    "float": float,
    "integer": int,
    "int": int,
    "boolean": bool,
    "bool": bool,
    "object": json.loads,
    "list": json.loads,
    "array": json.loads,
}


class Parameter:
    """
    Parameter class.

    This class represents a python typed parameter.
    """

    def __init__(self, **kwargs):
        """
        Create a parameter instance.

        Creates a parameter object and set attributes.
        """
        self.default = None
        self.required = False
        self.__dict__.update(kwargs)


class Converter:
    """
    Converter class.

    This class contains various str to Python type conversions.
    """

    @staticmethod
    def as_str(req, name, default=None, required=False, **_kwargs):
        """
        Get the parameter as a string.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param str default:     Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return str:            Converted parameter value
        """
        return req.get_param(name, default=default, required=required)

    @staticmethod
    def as_float(req, name, default=None, required=False, **_kwargs):
        """
        Get the parameter as a float.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param float default:   Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return float:          Converted parameter value
        """
        default = float(default) if default else None
        return req.get_param_as_float(name, default=default, required=required)

    @staticmethod
    def as_int(req, name, default=None, required=False, **_kwargs):
        """
        Get the parameter as an integer.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param int default:     Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return int:            Converted parameter value
        """
        default = int(default) if default else None
        return req.get_param_as_int(name, default=default, required=required)

    @staticmethod
    def as_bool(req, name, default=None, required=False, **_kwargs):
        """
        Get the parameter as a boolean.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param bool default:    Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return bool:           Converted parameter value
        """
        return req.get_param_as_bool(name, default=default, required=required)

    @staticmethod
    def as_object(req, name, default=None, required=False, **_kwargs):
        """
        Get the parameter as an object.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param dict default:    Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return:                Converted parameter value
        """
        return req.get_param_as_json(name, default=default, required=required)

    @staticmethod
    def as_list(req, name, default=None, required=False, transform=None, **_kwargs):
        """
        Get the parameter as a list.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param list default:    Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :param transform:       Function to transform the list items
        :return:                Converted parameter value
        """
        # if param is a string, convert to list and strip whitespace
        # handles cases where commas were encoded and bypassed Falcon's built-in conversion
        # also removes empty strings from list
        if isinstance(req.params[name], str) and req.params[name]:
            req.params[name] = [x.strip() for x in req.params[name].split(",")]

        # convert to list, if needed
        if not isinstance(req.params[name], list):
            req.params[name] = list(req.params[name])

        items = req.get_param_as_list(name, default=default, required=required, transform=transform)

        return [item for item in items if item != ""]

    @staticmethod
    def as_array(req, name, default=None, required=False, transform=None, **_kwargs):
        """
        Get the parameter as a list.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param list default:    Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :param transform:       Function to transform the list items
        :return:                Converted parameter value
        """
        Converter.as_list(req, name, default=default, required=required, transform=transform)

    @staticmethod
    def convert(req, parameter, transform=None):
        """
        Convert parameter types to Python types.

        :param Request req:          Request object
        :param Parameter parameter:  Parameter object
        :param str transform:        Transform method name
        :return:                     None
        """
        converter = getattr(Converter, f"as_{parameter.datatype}", Converter.as_str)
        transform = TRANSFORMS.get(transform, str)
        default = transform(parameter.default) if transform and parameter.default else None

        return converter(
            req,
            parameter.name,
            default=default,
            required=parameter.required,
            transform=transform,
        )


class ProcessParams:
    """This middleware will process parameters and convert them to python types."""

    def _check_required(self, request, parameter):
        """
        Check if specified parameter is required.

        If the specified parameter is required and not present,
        raise the appropriate HTTP error.

        :param Request request:         Request object:
        :param Parameter parameter:     Parameter object
        :return:                        None
        :raises falcon.HTTPBadRequest:  Falcon bad request exception
        """
        value = parameter.default or request.params.get(parameter.name)
        if parameter.required and not value:
            raise falcon.HTTPBadRequest(
                title="Bad Request",
                description=f"Missing parameter {parameter.name}",
            )

    def _convert(self, request, parameter):
        pass

    def _parse_operators(self, request):
        operators = {}
        name = ""

        for param in list(request.params.keys()):
            name, _, operator = param.partition("__")
            if operator:
                operators[name] = operator
                request.params[name] = request.params.pop(param)

        return operators

    @staticmethod
    def get_resource_parameters(request, resource):
        """
        Return resource parameters.

        Return the resource parameter data dictionary.

        :param Request request:            Request object
        :param Response response:          Response object
        :return list[dict]                 Return list of parameter dictionaries
        """
        try:
            endpoint = request.uri_template
            method = request.method.lower()
            params = resource.__data__[endpoint][method]["parameters"]
        except (TypeError, AttributeError, KeyError):
            params = []

        return [Parameter(**x) for x in params]

    def process(self, request, parameters):
        """
        Process parameters.

        Process, validate, and type convert to python types.

        :param Request request:             Request object
        :param list[Parameter] parameters:  List of parameters from the schema
        :return:                            None
        """
        transform = None
        operators = self._parse_operators(request)

        # include operator if found and update parameter names
        if operators:
            request.params["operators"] = parameters.operators = operators

        # use the docs schema to validate
        for parameter in parameters:
            present = parameter.name in request.params

            # check for required parameters
            self._check_required(request, parameter)

            # if parameter is not required, not specified, and has no default, move on
            if not present and not parameter.default:
                continue

            # for operators in and between, datatype must be a list
            if operators.get(parameter.name) in ["in", "between"]:
                parameter.datatype = "list"
                transform = parameter.datatype

            if m := re.search(r"list\[(\w+)]", parameter.datatype):
                parameter.datatype = "list"
                transform = m.group(1)

            request.params[parameter.name] = Converter.convert(
                request,
                parameter,
                transform=transform,
            )

    def process_resource(self, request, _response, resource, params):
        """
        Process resource.

        Process  the parameters for the request resource.

        :param Request request:     Request object
        :param Response _response:  Response object
        :param Resource resource:   Resource object
        :param list params:         Resource parameters
        :return:                    None
        """
        schema = self.get_resource_parameters(request, resource)

        # combine parameters from query, path, and body
        for media_params in [params, request.get_media(default_when_empty=None)]:
            if isinstance(media_params, dict):
                request.params.update(media_params)

        # if resource has no schema, skip further processing
        if not schema:
            return

        # process, validate, convert, etc
        self.process(request, schema)
