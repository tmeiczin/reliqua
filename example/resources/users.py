"""
Users resource — demonstrates the most common Reliqua features.

Features shown:
- Multiple routes on separate classes with suffix routing
- __routes__ dict with suffix option for multi-route resources
- __tags__ for OpenAPI grouping
- __auth__ for per-method role-based authorization
- no_auth = True to bypass authentication entirely
- Component schemas (user, users) referenced in :response docstrings
- Enum attributes referenced from docstring [enum=<attr>]
- Path parameters (in=path, required)
- Query parameters (in=query) with default values
- Typed list parameters: list[int], list[str], list[dict]
- Body parameters (in=body) with required, default, object types
- Multiple content types via :accepts and :return
- get_params() helper for extracting request parameters
- Resource attributes (self.version) and app config (self.app_config)
- Exception handling with HTTPNotFound

Copyright 2016-2024.
"""

from reliqua.exceptions import HTTPNotFound
from reliqua.resources.base import Resource

# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------

users = [
    {"username": "admin", "email": "admin@example.com", "role": "admin"},
    {"username": "alice", "email": "alice@example.com", "role": "viewer"},
    {"username": "bob", "email": "bob@example.com", "role": "viewer"},
]

# ---------------------------------------------------------------------------
# OpenAPI component schemas
# ---------------------------------------------------------------------------
# These are referenced by name in :response docstrings (e.g., :response 200 user:)
# and automatically added to the OpenAPI components/schemas section.

USER = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "examples": ["alice"]},
        "email": {"type": "string", "examples": ["alice@example.com"]},
        "role": {"type": "string", "examples": ["viewer"]},
    },
    "required": ["username", "email"],
}

USERS = {"type": "array", "items": {"$ref": "#/components/schemas/user"}}

# ---------------------------------------------------------------------------
# Enum values referenced by enum= option in docstrings
# ---------------------------------------------------------------------------

SORT_FIELDS = ["username", "email", "role"]
ROLES = ["admin", "viewer"]


class User(Resource):
    """Single user operations (get, update, delete by ID).

    Demonstrates:
    - Suffix routing: __routes__ maps /users/{id} with suffix="by_id",
      so handlers are named on_get_by_id, on_put_by_id, on_delete_by_id
    - __auth__ restricts PUT and DELETE to admin role only;
      GET has no restriction so the AccessResource default_mode applies
    - Path parameters with [in=path required]
    - Component schema reference in :response (user)
    - Multiple :accepts and :return content types
    """

    __routes__ = {
        "/users/{id}": {"suffix": "by_id"},
    }

    __tags__ = ["users"]

    __auth__ = {
        "PUT": ["admin"],
        "DELETE": ["admin"],
    }

    # Schema attributes referenced by :response docstrings
    user = USER

    def on_get_by_id(self, _req, resp, id=None):
        """
        Retrieve a user by ID.

        Returns a single user object matching the given ID.

        :param int id:          [in=path required] User ID (zero-indexed)

        :response 200 user:     User was retrieved
        :response 404:          User not found

        :return [json yaml]:
        """
        try:
            resp.media = users[int(id)]
        except (IndexError, ValueError, TypeError) as exc:
            raise HTTPNotFound(
                "User not found",
                description="Please provide a valid user ID.",
            ) from exc

    def on_put_by_id(self, req, resp, id=None):
        """
        Update a user by ID.

        Replaces the user at the given index. Requires admin role.

        :param int id:          [in=path required] User ID
        :param str username:    [in=body required] Username
        :param str email:       [in=body required] Email address
        :param str role:        [in=body default=viewer] User role

        :response 200 user:     User was updated
        :response 404:          User not found

        :accepts json:
        :return json:
        """
        try:
            idx = int(id)
            p = req.params
            users[idx] = {
                "username": p["username"],
                "email": p["email"],
                "role": p.get("role", "viewer"),
            }
            resp.media = users[idx]
        except (IndexError, ValueError, TypeError) as exc:
            raise HTTPNotFound("User not found") from exc

    def on_delete_by_id(self, _req, resp, id=None):
        """
        Delete a user by ID.

        Removes the user at the given index. Requires admin role.

        :param int id:          [in=path required] User ID

        :response 200:          User was deleted
        :response 404:          User not found

        :return json:
        """
        try:
            removed = users.pop(int(id))
            resp.media = {"deleted": removed["username"]}
        except (IndexError, ValueError, TypeError) as exc:
            raise HTTPNotFound("User not found") from exc


class Users(Resource):
    """Collection-level user operations (list and create).

    Demonstrates:
    - no_auth = True: this resource bypasses authentication entirely,
      regardless of the AccessResource default_mode
    - Query parameters with defaults, typed lists, and enum references
    - Body parameters with required, default, object, and typed list types
    - get_params() helper for extracting a subset of request parameters
    - Accessing self.app_config and self.version (resource_attributes)
    - Component schema reference for collection response (users)
    """

    __routes__ = {"/users": {}}

    __tags__ = ["users"]

    # Public endpoint — no authentication required
    no_auth = True

    # Schema attributes
    users = USERS

    # Enum attributes referenced by [enum=sort_fields] and [enum=roles]
    sort_fields = SORT_FIELDS
    roles = ROLES

    version = None

    def on_get(self, req, resp):
        """
        List users.

        Returns all users, optionally filtered by query parameters.
        This endpoint is public (no_auth = True).

        :param str username:        [in=query] Filter by username
        :param str email:           [in=query default=] Filter by email
        :param list[int] ids:       [in=query] Filter by list of user IDs
        :param str sort:            [in=query enum=sort_fields default=username] Sort field
        :param str role:            [in=query enum=roles] Filter by role

        :response 200 users:        Users were retrieved

        :accepts [json yaml]:
        :return [json yaml]:
        """
        p = req.params
        results = users

        # Filter by username
        if p.get("username"):
            results = [u for u in results if u["username"] == p["username"]]

        # Filter by email
        if p.get("email"):
            results = [u for u in results if u["email"] == p["email"]]

        # Filter by IDs
        if p.get("ids"):
            results = [users[i] for i in p["ids"] if i < len(users)]

        # Filter by role
        if p.get("role"):
            results = [u for u in results if u["role"] == p["role"]]

        resp.media = {
            "results": results,
            "count": len(results),
            "sort": p.get("sort", "username"),
            "version": self.version,
        }

    def on_post(self, req, resp):
        """
        Create a new user.

        Accepts a JSON body with user details. This endpoint is public.

        :param str username:        [in=body required] Username
        :param str email:           [in=body required] Email address
        :param str role:            [in=body default=viewer] User role
        :param list[str] tags:      [in=body] Optional tags for the user
        :param list[dict] metadata: [in=body] Optional metadata entries
        :param bool active:         [in=body default=true] Whether user is active
        :param object preferences:  [in=body] Arbitrary JSON preferences

        :response 201:              User was created
        :response 400:              Invalid request body

        :accepts json:
        :return json:
        """
        p = self.get_params(req, exclude=["tags", "metadata", "preferences"])
        users.append(p)
        resp.status = "201 Created"
        resp.media = {
            "id": len(users) - 1,
            "user": p,
        }
