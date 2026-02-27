# Reliqua

A simple, efficient, and intuitive Python REST API framework built on [Falcon](https://falconframework.org/) and [Gunicorn](https://gunicorn.org/). Define resources with Sphinx-style docstrings and Reliqua handles routing, parameter validation, type coercion, and OpenAPI 3.1 documentation automatically.

## Features

- **Automatic route discovery** — Resource modules are auto-loaded from a directory
- **OpenAPI 3.1 generation** — API docs generated from docstrings at startup
- **Built-in Swagger UI** — Interactive API explorer served at `/docs`
- **Parameter validation & type coercion** — Declared parameter types are automatically enforced
- **Pluggable authentication & authorization** — Basic, Cookie, Header, Query, and Bearer auth with role-based access control
- **CORS support** — Enabled by default
- **Database helpers** — MySQL, PostgreSQL, and SQLite via Peewee ORM
- **Custom media handlers** — JSON (with datetime support), YAML, and plain text

## Installation

```bash
pip install reliqua
```

### Dependencies

- `falcon>=3.0.0`
- `falcon-cors`
- `gunicorn>=19.6.0`
- `pyyaml`

Optional for database support: `peewee`

## Quick Start

### 1. Create a Resource

Resources are classes that subclass `Resource`. Routes, parameters, and responses are all defined via class attributes and docstrings.

```python
from reliqua.resources.base import Resource
from reliqua.exceptions import HTTPNotFound


users = [
    {"username": "ted", "email": "ted@nowhere.com"},
    {"username": "bob", "email": "bob@nowhere.com"},
]

USER = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "examples": ["billy"]}
    },
    "required": ["username"],
}

USERS = {"type": "array", "items": {"$ref": "#/components/schemas/user"}}


class User(Resource):
    """User resource."""

    __routes__ = {
        "/users/{id}": {"suffix": "by_id"},
    }

    __tags__ = ["users"]
    __auth__ = {"GET": ["admin"]}

    user = USER

    def on_get_by_id(self, req, resp, id=None):
        """
        Return a user.

        :param str id:         [in=path required] User ID
        :response 200 user:    User was retrieved
        :response 404:         User not found
        :return json:
        """
        try:
            resp.media = users[int(id)]
        except IndexError as exc:
            raise HTTPNotFound("User not found") from exc


class Users(Resource):
    """Users resource."""

    __routes__ = {"/users": {}}
    __tags__ = ["users"]

    users = USERS

    def on_get(self, req, resp):
        """
        Return users.

        :param str username:    [in=query] Username
        :param str email:       [in=query default=ted@nowhere.com] Email

        :response 200 users:    Users were retrieved
        :response 401:          Invalid Authorization
        :return json:
        """
        resp.media = {"results": users}

    def on_post(self, req, resp):
        """
        Create a new user.

        :param str username:    [in=body required] Username
        :param str email:       [in=body required] Email

        :accepts json:
        :return json:
        """
        users.append(req.params)
        resp.media = len(users) - 1
```

### 2. Create the Application

```python
from reliqua import Application

app = Application(
    resource_path="/path/to/resources",
    info={
        "title": "My API",
        "version": "1.0.0",
        "description": "My awesome API",
    },
    gunicorn={
        "bind": "127.0.0.1:8000",
        "workers": 2,
    },
)
app.run()
```

The OpenAPI UI will be available at:

```
http://127.0.0.1:8000/docs
```

The OpenAPI JSON spec will be available at:

```
http://127.0.0.1:8000/openapi/openapi.json
```

## Configuration

The `Application` constructor accepts the following option groups:

### `info` — API Metadata

| Key | Default | Description |
|---|---|---|
| `title` | `"Application Title"` | API title shown in docs |
| `version` | `"1.0.0"` | API version |
| `description` | `""` | API description |
| `license` | `""` | License name |
| `license_url` | `""` | License URL |
| `contact_name` | `""` | Contact name |

### `openapi` — Documentation Options

| Key | Default | Description |
|---|---|---|
| `ui_url` | `None` | Public URL for the API (e.g., behind a proxy). Defaults to `http://{bind}` |
| `highlight` | `True` | Enable syntax highlighting in Swagger UI |
| `sort` | `"alpha"` | Sort order for operations |
| `path` | `"/openapi"` | Path for OpenAPI spec endpoint |
| `docs` | `"/docs"` | Path for Swagger UI |
| `servers` | `[]` | Additional server entries for OpenAPI spec |

### `gunicorn` — Server Options

| Key | Default | Description |
|---|---|---|
| `bind` | `"127.0.0.1:8000"` | Address and port to listen on |
| `workers` | `1` | Number of worker processes |
| `worker_class` | `"gthread"` | Gunicorn worker class |
| `timeout` | `30` | Worker timeout in seconds |
| `keepalive` | `2` | Keep-alive timeout |
| `loglevel` | `"critical"` | Log level |
| `accesslog` | `"-"` | Access log target |
| `errorlog` | `"-"` | Error log target |

### Other Parameters

| Parameter | Default | Description |
|---|---|---|
| `resource_path` | `""` | Directory containing resource modules |
| `middleware` | `[]` | List of middleware instances |
| `config` | `None` | App config dict accessible on resources as `self.app_config` |
| `resource_attributes` | `{}` | Key/value pairs set as attributes on every resource |

## Resources

### Routes

Routes are defined as a dictionary on the `__routes__` class attribute. Keys are URL patterns and values are option dicts.

```python
class MyResource(Resource):
    __routes__ = {
        "/items": {},
        "/items/{id}": {"suffix": "by_id"},
    }

    def on_get(self, req, resp):
        """Handle GET /items."""

    def on_get_by_id(self, req, resp, id=None):
        """Handle GET /items/{id}."""
```

When a resource has multiple routes, the `suffix` option distinguishes handler methods (e.g., `on_get_by_id`, `on_delete_by_id`).

### Docstring Parameters

Parameters are declared using Sphinx-style docstrings:

```
:param <type> <name>:   [<options>] <description>
```

**Supported types:** `str`, `int`, `float`, `bool`, `list`, `list[int]`, `list[str]`, `list[dict]`, `object`, `dict`, `json`

**Options** (inside `[]`):

| Option | Description |
|---|---|
| `in=query\|path\|body\|form` | Parameter location (default: `query`) |
| `required` | Mark as required (path params are always required) |
| `default=<value>` | Default value |
| `enum=<attr>` | Resource attribute containing allowed values |
| `min=<n>` | Minimum value |
| `max=<n>` | Maximum value |

### Responses

```
:response <code> [<schema>]:   <description>
```

The optional `<schema>` name references a class attribute containing an OpenAPI schema dict. The schema is automatically added to the OpenAPI `components/schemas` section.

### Content Types

```
:return [json, yaml, xml]:      Response content types
:accepts [json, xml]:           Accepted request content types
```

Supported aliases: `json`, `yaml`, `xml`, `html`, `text`, `binary`, `gzip`, `form`, `jpeg`, `png`, `gif`

### Resource Attributes

| Attribute | Description |
|---|---|
| `__routes__` | Dict mapping URL patterns to route options |
| `__tags__` | List of OpenAPI tags (defaults to class name) |
| `__auth__` | Dict mapping HTTP methods to allowed roles |
| `__components__` | Dict of OpenAPI component schemas |
| `no_auth` | Set to `True` to bypass authentication |

### Helper Methods

The `Resource` base class provides `get_params(req, keys=None, exclude=None)` to extract request parameters.

## Authentication & Authorization

Reliqua separates authentication (identity verification) from authorization (access control).

### Authentication

```python
from reliqua.auth import (
    AuthenticationContext,
    AuthMiddleware,
    BasicAuthentication,
    CookieAuthentication,
    HeaderAuthentication,
    QueryAuthentication,
    MultiAuthentication,
)


def validate_user(username, password):
    if username == "admin" and password == "secret":
        return AuthenticationContext(user="admin", role="admin")
    return None


def validate_api_key(api_key):
    if api_key == "abc123":
        return AuthenticationContext(name="api_user", role="admin")
    return None


# HTTP Basic auth
basic_auth = BasicAuthentication(validation=validate_user)

# API key from cookie
cookie_auth = CookieAuthentication("api_key", validation=validate_api_key)

# API key from header
header_auth = HeaderAuthentication("X-API-Key", validation=validate_api_key)

# API key from query parameter
query_auth = QueryAuthentication("api_key", validation=validate_api_key)

# Try multiple authenticators in order
multi_auth = MultiAuthentication([basic_auth, cookie_auth])
```

Validation callbacks receive credentials and must return an `AuthenticationContext` on success or a falsy value on failure.

### Authorization

Four access control strategies are available:

**AccessResource** — Per-resource authorization via `__auth__` class attributes:

```python
from reliqua.auth import AccessResource, AuthMiddleware

control = AccessResource(default_mode="deny")
auth = AuthMiddleware([basic_auth], control=control)

class SecureResource(Resource):
    __auth__ = {
        "GET": ["admin", "user"],
        "POST": ["admin"],
    }
```

**AccessMap** — A centralized route-to-role mapping:

```python
from reliqua.auth import AccessMap

access_map = {
    "/users": {"GET": ["admin", "user"], "POST": ["admin"]},
    "/public": {"*": ["*"]},  # wildcard: any role, any method
}
control = AccessMap(access_map)
```

**AccessList** — Simple allow/deny lists of routes and methods:

```python
from reliqua.auth import AccessList

control = AccessList(
    routes=["/secret"],
    methods=["DELETE"],
    default_mode="allow",  # everything open except listed routes/methods
)
```

**AccessCallback** — Delegate to custom functions:

```python
from reliqua.auth import AccessCallback

control = AccessCallback(
    authenticate_callback=my_auth_check,
    authorized_callback=my_role_check,
)
```

### Applying Auth Middleware

```python
auth_middleware = AuthMiddleware([basic_auth, cookie_auth], control=control)

app = Application(
    resource_path="/path/to/resources",
    middleware=[auth_middleware],
)
```

Resources with `no_auth = True` bypass authentication entirely. The authenticated context is available in handlers via `req.context["authentication"]`.

## Database Support

Database helpers use the [Peewee ORM](http://docs.peewee-orm.com/) with a proxy pattern.

```python
from reliqua.database import BaseModel, mysql_connect, DatabaseConnection
import peewee

# Connect to the database
db = mysql_connect("localhost", "mydb", "user", "password", 3306)

# Define a model
class UserModel(BaseModel):
    username = peewee.CharField()
    email = peewee.CharField()

# Add DatabaseConnection middleware to manage connections per request
app = Application(
    resource_path="/path/to/resources",
    middleware=[DatabaseConnection()],
)
```

Available connection helpers: `mysql_connect()`, `psql_connect()`, `sqlite_connect()`

## Media Handlers

Built-in handlers are registered automatically:

| Content Type | Handler | Notes |
|---|---|---|
| `application/json` | `JSONHandler` | Serializes `datetime`, `date`, and `time` objects |
| `application/yaml` | `YAMLHandler` | YAML via PyYAML |
| `text/html` | `TextHandler` | Plain text |
| `text/plain` | `TextHandler` | Plain text |

## Example Application

A full example application is included in the `example/` directory demonstrating resources, authentication, form handling, and binary media streaming.

```bash
# Run the example
python -m example

# Custom bind address and port
python -m example --address 0.0.0.0 --port 9000
```

The Swagger UI will be available at `http://127.0.0.1:8000/docs`.

## License

MIT
