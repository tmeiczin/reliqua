import json
import inspect
import re

from falcon import status_codes


class Resource(object):

    def __init__(self):
        self.status_codes = status_codes

    def jsonify(self, data):
        return json.dumps(data)

    def _params(self, action):
        d = self.__schema__[self.__schema__.keys()[0]]
        return [x['name'] for x in d[action]['parameters']]

    def get_params(self, req, keys=None):
        p = {}

        caller = re.search('on_(\w+)', inspect.stack()[1][3]).group(1)

        if not keys:
            keys = self._params(caller)

        if req.content_length:
            for k in keys:
                p[k] = req.media.get(k)
        else:
            for k in keys:
                p[k] = req.get_param(k, default='')

        return p
