

def get_params_from_openapi(request, resource):
    """Get the resources parameters from the openapi docstring."""
    try:
        endpoint = request.uri_template
        method = request.method.lower()
        api_params = resource.__schema__[endpoint][method]["parameters"]
    except (TypeError, AttributeError, KeyError):
        api_params = []
    return api_params


class ProcessParams(object):

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
