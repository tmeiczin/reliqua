"""
Servers resource — demonstrates multi-route resources and path param coercion.

Features shown:
- Multiple routes on one class with suffix routing
- Integer path parameter type coercion (int cpus in=path)
- Query list parameters (list labs in=query)
- Float parameters with min/max constraints
- __auth__ with wildcard method (*) granting access to all verbs
- Multi-line docstring descriptions for OpenAPI
- Raising HTTPNotFound exceptions

Copyright 2016-2024.
"""

from reliqua.exceptions import HTTPNotFound
from reliqua.resources.base import Resource

# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------

servers = [
    {"name": "romeo", "cpus": 4, "memory_gb": 16.0, "location": "us-east"},
    {"name": "juliet", "cpus": 8, "memory_gb": 32.0, "location": "us-west"},
    {"name": "hamlet", "cpus": 16, "memory_gb": 64.0, "location": "eu-west"},
    {"name": "ophelia", "cpus": 2, "memory_gb": 8.0, "location": "us-east"},
]

LOCATIONS = ["us-east", "us-west", "eu-west", "ap-south"]


class Server(Resource):
    """Single server operations by ID.

    Demonstrates:
    - Suffix routing for /servers/{id}
    - __auth__ with wildcard: all methods require admin role
    - Integer path parameter
    """

    __routes__ = {
        "/servers/{id}": {"suffix": "by_id"},
    }

    __tags__ = ["servers"]

    __auth__ = {
        "*": ["admin"],
    }

    def on_get_by_id(self, _req, resp, id=None):
        """
        Retrieve a server by ID.

        Returns detailed information about a specific server.

        :param int id:          [in=path required] Server ID (zero-indexed)

        :response 200:          Server was retrieved
        :response 404:          Server not found

        :return json:
        """
        try:
            resp.media = servers[int(id)]
        except (IndexError, ValueError, TypeError) as exc:
            raise HTTPNotFound("Server not found") from exc


class Servers(Resource):
    """Server collection and filtered queries.

    Demonstrates:
    - Two routes on one class: /servers and /servers/cpus/{cpus}
    - Suffix routing for the /cpus/{cpus} sub-route
    - Query list params for filtering
    - Enum parameter referencing a class attribute
    - Float parameter with min/max constraints
    - Integer path parameter with type coercion
    """

    __routes__ = {
        "/servers": {},
        "/servers/cpus/{cpus}": {"suffix": "by_cpu"},
    }

    __tags__ = ["servers"]

    __auth__ = {
        "GET": ["admin", "viewer"],
    }

    # Enum values referenced by [enum=locations]
    locations = LOCATIONS

    def on_get(self, req, resp):
        """
        List servers.

        Returns all servers, optionally filtered by location or
        minimum memory. Supports query list parameters and
        float constraints.

        :param list location:       [in=query enum=locations] Filter by datacenter location(s)
        :param float min_memory:    [in=query min=0 max=1024] Minimum memory in GB

        :response 200:              Servers were retrieved
        :response 400:              Invalid query parameter

        :return json:
        """
        p = req.params
        results = servers

        if p.get("location"):
            locs = p["location"] if isinstance(p["location"], list) else [p["location"]]
            results = [s for s in results if s["location"] in locs]

        if p.get("min_memory") is not None:
            results = [s for s in results if s["memory_gb"] >= p["min_memory"]]

        resp.media = {"results": results, "count": len(results)}

    def on_get_by_cpu(self, _req, resp, cpus=1):
        """
        List servers by CPU count.

        Returns servers that have at least the specified number of CPUs.
        The cpus path parameter is automatically coerced to int.

        :param int cpus:        [in=path required] Minimum number of CPUs

        :response 200:          Servers were retrieved
        :response 404:          No servers found

        :return json:
        """
        try:
            min_cpus = int(cpus)
        except (ValueError, TypeError) as exc:
            raise HTTPNotFound("Invalid CPU count") from exc

        results = [s for s in servers if s["cpus"] >= min_cpus]
        if not results:
            raise HTTPNotFound("No servers found with that CPU count")

        resp.media = {"results": results, "count": len(results)}
