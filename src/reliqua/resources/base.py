"""
Reliqua framework.

Copyright 2016-2024.
"""


class Resource:
    """
    Base resource class.

    All resource should be a subclass of Resource. This is how
    the application finds and adds routes.
    """

    def __init__(self, **kwargs):
        """
        Create Resource instance.

        Create the API resource instance.

        :param dict config:      Application configuration
        :return:                 None
        """
        self.__dict__.update(kwargs)

    @property
    def name(self):
        """Return class name."""
        return self.__class__.__name__

    def get_params(self, req, keys=None, exclude=None):
        """
        Retrieve the params from the request.

        :param Request req:    The request
        :param list keys:      List of params to get
        :param list exclude:   List of params to exclude
        :return dict:          Dictionary of parameters
        """
        params = {}
        exclude = exclude or []
        for param in req.params:
            if (not keys or param in keys) and param not in exclude:
                params[param] = req.params[param]
        return params
