import inspect
import re


def default_responses():

    default_responses = {
        '200': {
            'description': 'Successful operation',
        },
        '400': {
            'description': 'Bad input values',
        },
    }
    return default_responses


class Docs(object):

    __schema__ = {
        'swagger': '2.0',
        'info': {
            'description': 'application description',
            'version': '0.0.0',
            'title': 'application',
        },
        'host': '127.0.0.1:8000',
        'basePath': '',
        'schemes': [
            'http',
            'https',
        ],
        'consumes': [
            'application/json',
        ],
        'produces': [
            'application/json',
        ]
    }

    def __init__(
            self,
            resources,
            desc=None,
            version=None,
            title=None,
            host=None,
            base_path=None):

        schema = self.__schema__
        schema['paths'] = {}
        info = schema['info']
        info['description'] = desc or info['description']
        info['version'] = version or info['version']
        info['title'] = version or info['title']
        schema['host'] = host or schema['host']
        schema['basePath'] = base_path or schema['basePath']

        self.process_resources(resources)

    def process_resources(self, resources):
        for c in resources:
            c.__schema__ = {}
            for route in c.__routes__:
                c.__schema__[route] = self.route_schema(c, route)
                self.__schema__['paths'].update(c.__schema__)

    def route_schema(self, resource, route):
        verbs = ['get', 'put', 'post', 'delete']
        schema = {}

        for verb in verbs:
            method = getattr(resource, 'on_%s' % (verb), None)
            if not method:
                continue

            if not method.__doc__:
                continue

            operation_id = '%s%s' % (verb, resource.__name__.capitalize())
            tags = [resource.__name__.lower()]
            responses = default_responses()
            parameters = []

            doc = inspect.cleandoc(method.__doc__)
            match = re.search(r'(.*?):', doc, re.MULTILINE | re.DOTALL)

            if match:
                description = match.group(1).replace('\n', ' ')
            else:
                description = resource.__name__.capitalize()

            matches = re.finditer(r'^:(?P<token>|param|response|return)\s+(?P<token_fields>.*):\s+(?P<desc>[^:]*)', doc, re.MULTILINE)
            for match in matches:
                m = match.groupdict()
                if m['token'] == 'param':
                    parameters.append(self.process_parameter(resource, m))
                if m['token'] == 'response':
                    responses.update(self.process_response(resource, m))

            schema[verb] = {
                'description': description,
                'operationId': operation_id,
                'tags': tags,
                'parameters': parameters,
                'responses': responses
            }

        return schema

    def process_response(self, resource, r):
        response_code = r['token_fields']
        desc = r['desc']
        response = {
            response_code: {
                'description': desc
            }
        }

        return response

    def request_body(self, resource, p):
        pass

    def process_parameter(self, resource, m):
        required = False
        enum = None
        attributes = []
        where = 'query'
        token_type, token_name = m['token_fields'].split()

        match = re.match(r'\[(.*)\]\s+(.*)', m['desc'])
        if match:
            attributes, description = match.groups()
            attributes = re.split(r',\s+', attributes)
        else:
            description = m['desc']

        if token_type == 'str':
            token_type = 'string'

        for a in attributes:
            if a.startswith('in_'):
                where = a.replace('in_', '')
            if a == 'required':
                required = True
            if a == 'enum':
                enum = getattr(resource, token_name, [])

        parameter = {
            'name': token_name,
            'in': where,
            'description': description,
            'required': required,
            'type': token_type,
        }

        if enum:
            parameter['enum'] = enum

        return parameter

    def on_get(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.media = self.__schema__
