from reliqua.resources.base import Resource
from reliqua.status_codes import HTTP


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

phones = ['603-555-1234', '603-555-5678']


class User(Resource):

    __routes__ = {
        "/users/{id}": {
            "suffix": "by_id"
        },
    }

    __tags__ = [
       "users",
    ]

    phones = phones

    def on_get_by_id(self, req, resp, id=None):
        """
        Retrieve a user.

        :param str id:       [in_path, required] User ID
        :param str email:    [in_query] User Email
        :param str|int phone:    [in_query, enum=phones] Phone Numbers

        :response 200:       user was retrieved
        :response 400:       invalid query paremeter

        :return json:
        """
        try:
            resp.media = users[int(id)]
        except IndexError:
            resp.status = HTTP('404')

    def on_delete_by_id(self, req, resp, id=None):
        """
        Delete a user.

        :param str id:      [in_path] User Id

        :return json:
        """
        try:
            users.pop(int(id))
            resp.media = {'success': True}
        except IndexError:
            resp.status = HTTP('400')


class Users(Resource):

    __routes__ = {
        '/users': {},
        '/employees': {},
    }

    __tags__ = [
       "users",
    ]

    def on_get(self, req, resp):
        """
        Retrieve a user

        :param str username:      [in_query required]  Username
        :param str email:         [in_query default=terrence.meiczinger@hpe.com]  Email

        :return json:
        """
        results = []
        p = req.params
        print(p)
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
        """
        Delete a user.

        :param str id:      [in_query, required] User Id

        :return json:
        """
        p = req.params
        try:
            users.pop(int(p.get(id, None)))
            resp.media = {'success': True}
        except IndexError:
            resp.status = HTTP('400')

    def on_post(self, req, resp):
        """
        Create a new user

        :param str username:      [in_body, required]  Username
        :param str email:         [in_body, required]  Email

        :return json:
        """
        p = req.params
        users.append(p)
        resp.media = len(users) - 1
