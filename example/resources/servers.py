"""
Reliqua Framework.

Copyright 2016-2024.
"""

from reliqua.exceptions import HTTPNotFound
from reliqua.resources.base import Resource

servers = [
    "romeo",
    "juliet",
]


class Server(Resource):
    """Server resource."""

    __routes__ = {
        "/servers/{id}": {"suffix": "by_id"},
    }

    __tags__ = [
        "servers",
    ]

    def on_get_by_id(self, _req, resp, id=None):
        """
        Retrieve a server.

        Retrieve a server by its ID.

        :param str id:       [in=path, required] Server ID

        :response 200:       Server was retrieved
        :response 404:       Server not found

        :return json:
        """
        try:
            resp.media = servers[int(id)]
        except (IndexError, ValueError):
            raise HTTPNotFound("Invalid ID")


class Servers(Resource):
    """Servers resource."""

    __routes__ = {"/servers": {}, "/servers/cpus/{cpus}": {"suffix": "by_cpu"}}

    __tags__ = [
        "servers",
    ]

    def on_get(self, req, resp):
        """
        Retrieve servers.

        Retrieve a list of servers in the lab.

        :param list labs:     [in=query] The labs servers are located

        :response 200:        Servers were retrieved
        :response 400:        Invalid query parameter

        :return json:
        """
        labs = req.params.get("labs")
        resp.media = labs

    def on_get_by_cpu(self, _req, resp, cpus=1):
        """
        Retrieve a server by CPU.

        Retrieve server information by CPU.

        :param int cpus:     [in=path required] Number of CPUs for server

        :response 200:       Server was retrieved
        :response 404:       Server not found

        :return json:
        """
        try:
            resp.media = servers[int(cpus)]
        except (IndexError, ValueError):
            raise HTTPNotFound("Invalid ID")
