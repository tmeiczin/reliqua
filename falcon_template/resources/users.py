from falcon_template.resources.base import Resource


users = [
    {
        'username': 'ted',
        'email': 'ted@nowhere.com',
    },
    {
        'username': 'bob',
        'email': 'bob@nowhere.com',
    }
]


class Users(Resource):

    __schema__ = {
        '/users': {
            'get': {
                'description': 'list all users',
                'operationId': 'listUsers',
                'tags': [
                    'users'
                ],
                'parameters': [
                    {
                        'name': 'username',
                        'in': 'query',
                        'description': 'Filter by username',
                        'required': False,
                        'type': 'string'
                    },
                    {
                        'name': 'email',
                        'in': 'query',
                        'description': 'Filter by email',
                        'required': False,
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
            'post': {
                'description': 'Create a new user',
                'operationId': 'addUser',
                'tags': [
                    'users'
                ],
                'parameters': [
                    {
                        'name': 'usermame',
                        'in': 'query',
                        'description': 'username of the user',
                        'required': True,
                        'type': 'string'
                    },
                    {
                        'email': 'email',
                        'in': 'query',
                        'description': 'user email address',
                        'required': True,
                    }
                ],
                'responses': {
                    '405': {
                        'description': 'Invalid input'
                    }
                },
            },
            'delete': {
                'description': 'Delete user',
                'operationId': 'deleteUser',
                'tags': [
                    'users'
                ],
                'parameters': [
                    {
                        'name': 'id',
                        'in': 'path',
                        'description': 'user id',
                        'required': True,
                        'type': 'int'
                    },
                ],
                'responses': {
                    '400': {
                        'description': 'Invalid input values'
                    }
                },
            },
        }
    }

    def on_get(self, req, resp, id=None):
        p = self.get_params(req)
        results = []
        if any(p.values()):
            for user in users:
                if user['username'] == p.get('username', None):
                    results.append(user)
                elif user['email'] == p.get('email', None):
                    results.append(user)
        else:
            results = users

        resp.body = self.jsonify(results)

    def on_post(self, req, resp):
        p = self.get_params(req)
        result = p
        resp.body = self.jsonify({'success': result})

    def on_delete(self, req, resp):
        p = self.get_params(req)
        result = p
        resp.body = self.jsonify({'success': result})
