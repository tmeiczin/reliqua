import falcon
import json


class ProcessParams(object):

    def process_resource(self, request, response, resource, params):
        try:
            endpoint = resource.__schema__.keys()[0]
            method = request.method.lower()
            api_params = resource.__schema__[endpoint][method]['parameters']
        except (AttributeError, KeyError) as e:
            e = e
            api_params = []

        if request.content_length:
            data = request.media
        else:
            data = request.params

        data.update(params)

        for p in api_params:
            name = p['name']
            required = p['required']

            if required and name not in data:
                raise falcon.HTTPBadRequest('Missing parameter %s' % (name), 'Bad Request')

            request.params[name] = data.get(name, '')


class JsonResponse(object):

    def process_response(self, req, resp, resource, req_succeeded):
        data = getattr(resp, 'json', None)
        if data is not None:
            resp.body = json.dumps(data)
