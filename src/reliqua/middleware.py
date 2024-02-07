import json
import falcon


def get_params_from_openapi(request, resource):
    """Get the resources parameters from the openapi docstring."""
    try:
        endpoint = request.uri_template
        method = request.method.lower()
        api_params = resource.__schema__[endpoint][method]["parameters"]
    except (TypeError, AttributeError, KeyError):
        api_params = []
    return api_params


class ProcessParams:
    """
    This middleware will process parameters and convert them to python types.

    This middleware is used by default in all unrest applications.
    """

    @staticmethod
    def get_param_as_string(req, name, default, required):
        """
        Get the parameter as a string.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param str default:     Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return:                Converted parameter value
        """
        return req.get_param(name, default=default, required=required)

    @staticmethod
    def get_param_as_float(req, name, default, required):
        """
        Get the parameter as a float.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param float default:   Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return:                Converted parameter value
        """
        if default is not None:
            default = float(default)
        return req.get_param_as_float(name, default=default, required=required)

    @staticmethod
    def get_param_as_int(req, name, default, required):
        """
        Get the parameter as an integer.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param int default:     Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return:                Converted parameter value
        """
        if default is not None:
            default = int(default)
        return req.get_param_as_int(name, default=default, required=required)

    @staticmethod
    def get_param_as_bool(req, name, default, _):
        """
        Get the parameter as a boolean.

        :param req:             Request object
        :param str name:        Name of the parameter
        :param bool default:    Default value of the parameter
        :param bool required:   ``True`` if the parameter is required else ``False``
        :return:                Converted parameter value
        """
        value = req.params.get(name, default)
        if value is True or str(value).lower() in ["true", "t", "0"]:
            return True
        if value is False or str(value).lower() in ["false", "f", "0"]:
            return False
        if value is None or str(value).lower() in ["", "none", "null"]:
            return None
        return value

    @staticmethod
    def get_param_as_object(req, name, default, required):
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
    def get_param_as_list(req, name, default, required, transform=None):
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
        items = req.get_param_as_list(
            name, default=default, required=required, transform=transform
        )
        return [item for item in items if item != ""]

    def __init__(self):
        """Create ProcessParams instance."""
        self.converters = {
            "string": self.get_param_as_string,
            "number": self.get_param_as_float,
            "integer": self.get_param_as_int,
            "boolean": self.get_param_as_bool,
            "object": self.get_param_as_object,
            "list": self.get_param_as_list,
            "array": self.get_param_as_list,
        }
        self.transforms = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "object": json.loads,
            "list": json.loads,
            "array": json.loads,
        }

    def process(self, request, api_params):
        """
        Process parameters and convert to python types.

        :param request:             Request object
        :param list api_params:     List of parameter dicts from the openapi spec
        """
        # split out operators
        operators = {}
        for param in list(request.params.keys()):
            name, _, operator = param.partition("__")
            if operator:
                operators[name] = operator
                request.params[name] = request.params.pop(param)

        # include operator dict in params if operators are found
        if operators:
            request.params["operators"] = operators

        # use the openapi schema to validate
        for param in api_params:
            name = param["name"]
            required = param["required"]
            default = param["schema"].get("default", None)
            datatype = param["schema"].get("type")
            present = name in request.params
            has_default = "default" in param["schema"]

            if required and not present and not has_default:
                raise falcon.HTTPBadRequest(
                    description=f"Missing parameter {name}", title="Bad Request"
                )

            if not required and not present and not has_default:
                # don't include parameter if it's neither required, present, nor has a given default value
                continue

            converter = self.converters.get(datatype, self.get_param_as_string)

            # if using the 'between' or 'in' operator, parse the value as a list
            if operators.get(name) in ["in", "between"]:
                request.params[name] = self.get_param_as_list(
                    request,
                    name,
                    default,
                    required,
                    transform=self.transforms.get(datatype),
                )
            else:
                request.params[name] = converter(request, name, default, required)

    def process_resource(self, request, response, resource, params):
        """
        Process resource.

        :param request:         Request object
        :param response:        Response object
        :param resource:        Resource object
        :param params:          Resource parameters
        """
        api_params = get_params_from_openapi(request, resource)

        # augment request.params with all params that were passed in
        for params_dict in [params, request.get_media(default_when_empty=None)]:
            if params_dict and isinstance(params_dict, dict):
                request.params.update(params_dict)

        # no openapi, just params and leave
        if not api_params:
            return

        self.process(request, api_params)

    async def process_resource_async(self, request, response, resource, params):
        """
        Process resource asynchronously.

        :param request:         Request object
        :param response:        Response object
        :param resource:        Resource object
        :param params:          Resource parameters
        """
        api_params = get_params_from_openapi(request, resource)

        # augment request.params with all params that were passed in
        for params_dict in [params, await request.get_media(default_when_empty=None)]:
            if params_dict:
                request.params.update(params_dict)

        # no openapi, just params and leave
        if not api_params:
            return

        self.process(request, api_params)
