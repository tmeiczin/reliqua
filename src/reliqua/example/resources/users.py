from reliqua.resources.base import Resource


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

phone = ['207-827-0028']


class User(Resource):

    __routes__ = [
        '/users/{id}',
    ]

    phone = phone

    def on_get(self, req, resp, id=None):
        """
        Retrieve a user.

        :param str id:       [in_path, required] User ID
        :param str email:    [in_query] User Email
        :param str phone:    [in_query, enum] Phone Numbers

        :response 200:
        :response 400:

        :return json:
        """
        try:
            resp.media = users[int(id)]
        except IndexError:
            resp.status = '404'

    def on_delete(self, req, resp, id=None):
        """
        Delete a user.

        :param str id:      [in_path, required] User Id

        :response 200:
        :response 400:
        :return json:
        """
        try:
            users.pop(int(id))
            resp.media = {'success': True}
        except IndexError:
            resp.status = '400'


class Users(Resource):

    __routes__ = [
        '/users',
    ]

    def on_get(self, req, resp):
        """
        Retrieve a user

        :param str username:      [in_query, required] Username
        :param str email:         [in_query]  Email

        :response 200:
        :response 400:

        :return json:
        """
        results = []
        p = req.params
        if any(p.values()):
            for user in users:
                if user['username'] == p.get('username', None):
                    results.append(user)
                elif user['email'] == p.get('email', None):
                    results.append(user)
        else:
            results = users

        resp.media = results

    def on_delete(self, req, resp):
        p = req.params
        try:
            users.pop(int(p.get(id, None)))
            resp.media = {'success': True}
        except IndexError:
            resp.status = '400'

    def on_post(self, req, resp):
        p = req.params
        users.append(p)
        resp.media = len(users) - 1
