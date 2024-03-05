"""
Reliqua Framework.

Copyright 2016-2024.
"""

import binascii
import os
from base64 import b64decode, b64encode

from peewee import (
    Model,
    MySQLDatabase,
    PostgresqlDatabase,
    Proxy,
    SqliteDatabase,
)

db = Proxy()


def is_b64(string):
    """
    Check if string is base64 encoded.

    :param str s:   String to check
    :return:        True if string is base64 encoded
    """
    try:
        return b64encode(b64decode(string)) == string
    except (ValueError, TypeError, binascii.Error):
        return False


class BaseModel(Model):
    """Base model class for applications using a PeeWee DB ORM."""

    class Meta:
        """Base metaclass."""

        database = db


class DatabaseConnection:
    """
    This middleware will handle the session connect and disconnect to the database.

    This is primarily needed for MySQL databases where the connections
    timeout, but the session does not.
    """

    def __init__(self, database):
        """Create DatabaseConnection instance."""
        self.db = database

    def process_request(self, _req, _resp):
        """
        Process the request.

        :param req:                 Request object
        :param resp:                Response object
        """
        self.db.connect()

    def process_response(self, _req, _resp, _resource, _req_succeeded):
        """
        Process the response.

        :param req:                 Request object
        :param resp:                Response object
        :param resource:            Resource object
        :param bool req_succeeded:  ``True`` if request succeeded else ``False``
        """
        if not self.db.is_closed():
            self.db.close()


def mysql_connect(host=None, database=None, user=None, password=None, port=3306):
    """
    Connect to MySQL database.

    :param str database:    Database Name
    :param str user:        User
    :param str password:    Password
    :param str host:        Host
    :param str port:        Port

    :return:                MySQLDatabase
    """
    if is_b64(password):
        password = b64decode(password)
    mysql = MySQLDatabase(database, user=user, password=password, host=host, port=port)
    db.initialize(mysql)

    return db


def psql_connect(host=None, database=None, user=None, password=None, port=5432):
    """
    Connect to PostgreSQL database.

    :param str database:    Database Name
    :param str user:        User
    :param str password:    Password
    :param str host:        Host
    :param str port:        Port

    :return:                PostgresqlDatabase
    """
    if is_b64(password):
        password = b64decode(password)
    mysql = PostgresqlDatabase(database, user=user, password=password, host=host, port=port)
    db.initialize(mysql)

    return db


def sqlite_connect(path):
    """
    Connect to SQLite database.

    :param str path:       Path to database file

    :return:               SqliteDatabase
    """
    path = os.path.expanduser(path)
    database = SqliteDatabase(path)
    db.initialize(database)

    return db
