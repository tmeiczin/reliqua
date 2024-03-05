"""
Reliqua framework.

Copyright 2016-2024.
"""

import inspect
import re


class Resource:

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
