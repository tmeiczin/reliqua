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

    def on_get_by_id(self, req, resp, id=None):
        """
        Retrieve servers.

        Retrieve a list of servers in the lab.

        :param str id:       [in=path, required] Server ID

        :response 200:       server was retrieved
        :response 400:       invalid query paremeter

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

        :param int cpus:     [in=query, required] Number of CPUs for server

        :response 200:       server  was retrieved
        :response 400:       invalid query paremeter

        :return json:
        """
        index = req.params.get("cpus")
        try:
            resp.media = servers[index]
        except IndexError:
            resp.status = HTTP("404")
        except TypeError:
            resp.media = servers

    def on_get_by_cpu(self, req, resp, cpu=1):
        """
        Retrieve a server by cpu.

        Retrieve server information by cpu

        :param int cpus:     [in=path, required] Number of CPUs for server

        :response 200:       server  was retrieved
        :response 400:       invalid query paremeter

        :return json:
        """
        try:
            resp.media = servers[int(id)]
        except IndexError:
            resp.status = HTTP("404")
