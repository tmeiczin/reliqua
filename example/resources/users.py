"""
Reliqua Framework.

Copyright 2016-2024.
"""

from reliqua.exceptions import HTTPNotFound
from reliqua.resources.base import Resource

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

USER = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "examples": ["billy"],
        }
    },
    "required": ["username"],
}

USERS = {"type": "array", "items": {"$ref": "#/components/schemas/user"}}


class User(Resource):
    """User resource."""

    __routes__ = {
        "/users/{id}": {"suffix": "by_id"},
    }

    __tags__ = [
        "users",
    ]

    __auth__ = {
        "put": ["admin"],
    }

    user = USER
    phones = phones

    def on_get_by_id(self, _req, resp, id=None):
        """
        Return a user.

        :param str id:         [in=path required] User ID
        :response 200 user:    User was retrieved
        :response 400:         Invalid query parameter
        :accepts [json,xml]:   Accept types
        :return [json,xml]:    Return content type
        """
        try:
            resp.media = users[int(id)]
        except IndexError as exc:
            raise HTTPNotFound("User not found", description="Please provide a valid user ID.") from exc

    def on_delete_by_id(self, _req, resp, id=None):
        """
        Delete a user.

        :param str id:      [in=path] User Id

        :return json:
        """
        try:
            users.pop(int(id))
            resp.media = {"success": True}
        except IndexError as exc:
            raise HTTPNotFound("User not found", description="Please provide a valid user ID.") from exc


class Users(Resource):
    """Users resource."""

    __routes__ = {
        "/users": {},
    }

    __tags__ = [
        "users",
    ]

    __auth__ = {
        "GET": ["admin"],
        "POST": ["admin"],
        "DELETE": ["admin"],
    }

    no_auth = True

    users = USERS

    def on_get(self, req, resp):
        """
        Return users.

        :param str username:      [in=query]  Username
        :param str email:         [in=query default=ted@nowhere.com]  Email
        :param list[int] ids:     [in=query] List of IDs

        :response 200 users:      Users were retrieved
        :response 401:            Invalid Authorization
        :accepts [json,xml]:      Accept types
        :return [json xml]:       Return JSON of users
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

        resp.media = {"results": results, "config": self.app_config, "random": self.random}

    def on_post(self, req, resp):
        """
        Create a new user.

        :param str username:      [in=body required=true]  Username
        :param str email:         [in=body required=true]  Email
        :param list[dict] data:   [in=body] Extra Data
        :param list[str] names:   [in=body] Names
        :param bool valid:        [in=body default=False] Valid
        :param object config:     [in=body] Configuration data

        :accepts [json xml]:      The body content type
        :return json:
        """
        p = req.params
        users.append(p)
        names = p.get("names")
        resp.media = len(users) - 1
