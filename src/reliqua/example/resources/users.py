from reliqua.resources.base import Resource
from reliqua.status_codes import HTTP

users = [
    {
        "username": "ted",
        "email": "ted@nowhere.com",
    },
    {
        "username": "bob",
        "email": "bob@nowhere.com",
    },
]

phones = ["603-555-1234", "603-555-5678"]


class User(Resource):

    __routes__ = {
        "/users/{id}": {"suffix": "by_id"},
    }

    __tags__ = [
        "users",
    ]

    phones = phones

    def on_get_by_id(self, req, resp, id=None):
        """
        Retrieve a user.

        :param str id:       [in=path, required] User ID

        :response 200:       user was retrieved
        :response 400:       invalid query paremeter

        :return json:
        """
        try:
            resp.media = users[int(id)]
        except IndexError:
            resp.status = HTTP("404")

    def on_delete_by_id(self, req, resp, id=None):
        """
        Delete a user.

        :param str id:      [in=path] User Id

        :return json:
        """
        try:
            users.pop(int(id))
            resp.media = {"success": True}
        except IndexError:
            resp.status = HTTP("400")


class Users(Resource):

    __routes__ = {
        "/users": {},
    }

    __tags__ = [
        "users",
    ]

    def on_get(self, req, resp):
        """
        Retrieve users.

        :param str username:      [in=query]  Username
        :param str email:         [in=query default=ted@invalid.com]  Email
        :param list[int] ids:     [in=query] List of IDs

        :return json:
        """
        results = []
        p = req.params
        if any(p.values()):
            for user in users:
                if user["username"] == p.get("username", None):
                    results.append(user)
                elif user["email"] == p.get("email", None):
                    results.append(user)
        else:
            results = users

        resp.media = results

    def on_post(self, req, resp):
        """
        Create a new user.

        :param str username:      [in=body, required]  Username
        :param str email:         [in=body, required]  Email

        :return json:
        """
        p = req.params
        users.append(p)
        resp.media = len(users) - 1
