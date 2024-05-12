"""
Reliqua Framework.

Copyright 2016-2024.
"""

from reliqua.resources.base import Resource
from reliqua.status_codes import HTTP

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
        Retrieve servers.

        Retrieve a list of servers in the lab.

        :param str id:       [in=path, required] Server ID

        :response 200:       server was retrieved
        :response 400:       invalid query parameter

        :return json:
        """
        try:
            resp.media = servers[id]
        except IndexError:
            resp.status = HTTP("404")


class Servers(Resource):
    """Servers resource."""

    __routes__ = {"/servers": {}, "/servers/cpus/{cpus}": {"suffix": "by_cpu"}}

    __tags__ = [
        "servers",
    ]

    def on_get(self, req, resp):
        """
        Retrieve a server.

        Retrieve server information

        :param list labs:     [in=query] The labs servers are located

        :response 200:       server  was retrieved
        :response 400:       invalid query parameter

        :return json:
        """
        labs = req.params.get("labs")
        resp.media = labs

    def on_get_by_cpu(self, _req, resp, cpus=1):
        """
        Retrieve a server by cpu.

        Retrieve server information by cpu

        :param int cpus:     [in=path, required] Number of CPUs for server

        :response 200:       server  was retrieved
        :response 400:       invalid query parameter

        :return json:
        """
        try:
            resp.media = servers[cpus]
        except IndexError:
            resp.status = HTTP("404")
