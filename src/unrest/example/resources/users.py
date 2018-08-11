from unrest.resources.base import Resource


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
                        'type': 'string'
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
        resp.body = self.jsonify(users[int(id)])

    def on_delete(self, req, resp, id=None):
        try:
            users.pop(int(id))
            resp.body = self.jsonify({'success': True})
        except IndexError:
            resp.status = '400'


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
                        'required': True,
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
                        'name': 'email',
                        'in': 'query',
                        'description': 'user email address',
                        'required': True,
                        'type': 'string'
                    }
                ],
                'responses': {
                    '405': {
                        'description': 'Invalid input'
                    }
                },
            },
        }
    }

    def on_get(self, req, resp, id=None):
        p = req.params
        results = []
        if any(p.values()):
            for user in users:
                if user['username'] == p.get('username', None):
                    results.append(user)
                elif user['email'] == p.get('email', None):
                    results.append(user)
        else:
            results = users

        resp.json = results

    def on_post(self, req, resp):
        p = req.params
        users.append(p)
        resp.json = len(users) - 1
