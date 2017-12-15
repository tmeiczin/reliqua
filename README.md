This is sample template to create a quick Python Falcon API application. It uses a schema defined in the resource for the route path and swagger documentation. The base application will handle creating the routes and documentation automatically at runtime.

You define a resource, then add a schema based on the OpenAPI specification.

from falcon_template.resources.base import Resource

class User(Resource):

    __schema__ = {
        '/users/{id}': {
            'get': {
                'description': 'retrieve users',
                'operationId': 'getUser',
                'tags': [
                    'users'
                ],
                'parameters': [
                    {
                        'name': 'id',
                        'in': 'path',
                        'description': 'User ID',
                        'required': True,
                        'type': 'string'
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'successful operation',
                        'examples': {
                            'application/json': {
                                'results': [
                                    {
                                        'username': 'fred',
                                        'email': 'fred@fake.com',
                                    }
                                ],
                                'success': True,
                            }
                        }
                    }
                }
            },
        }
    }

    def on_get(self, req, resp, id=None):
        resp.body = self.jsonify(users[int(id)])
