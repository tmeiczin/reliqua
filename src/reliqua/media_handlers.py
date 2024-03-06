"""
Reliqua Framework.

Copyright 2016-2024.
"""

import json
from datetime import date, datetime, time
from functools import partial

import falcon
import yaml
from falcon.media import BaseHandler
from falcon.media import JSONHandler as FalconJSONHandler
from yaml import SafeLoader


class YAMLHandler(BaseHandler):
    """Media handler class for YAML."""

    def deserialize(self, stream, _content_type, _content_length):
        """
        Load YAML from stream and return the appropriate Python object.

        :param stream:      stream to load from
        :return:            deserialized YAML as python object
        """
        try:
            return yaml.load(stream.read().decode("utf-8"), SafeLoader)
        except ValueError as exception:
            raise falcon.HTTPBadRequest(
                title="Invalid YAML",
                description=f"Could not parse YAML body: {exception}",
            ) from exception

    def serialize(self, media, _content_type):
        """
        Serialize media to YAML.

        :param media:       media to serialize
        :return:            serialized YAML
        """
        result = yaml.dump(media)

        try:
            result = result.encode("utf-8")
        except AttributeError:
            pass

        return result


class TextHandler(BaseHandler):
    """Media handler class for text."""

    def deserialize(self, stream, _content_type, _content_length):
        """
        Read text from stream.

        :param stream:      stream to load from
        :return:            text
        """
        try:
            return stream.read().decode("utf-8")
        except ValueError as exception:
            raise falcon.HTTPBadRequest(
                title="Invalid Text", description=f"Could not parse body: {exception}"
            ) from exception

    def serialize(self, media, _content_type):
        """
        Serialize media to text.

        :param media:       media to serialize
        :return:            serialized text
        """
        result = f"{media}"

        try:
            result = result.encode("utf-8")
        except AttributeError:
            pass

        return result


class JSONHandler(FalconJSONHandler):
    """
    Media handler class for JSON.

    Overloads the FalconJSONHandler to handle datetime objects.
    """

    def converter(self, obj):
        """
        Convert datetime objects to string.

        :param obj:     object to convert
        :return:        converted object
        """
        if isinstance(obj, (datetime, time, date)):
            return str(obj)
        return obj

    def __init__(self, dumps=None, loads=None):
        """Create JSONHandler instance."""
        dumps = dumps or partial(json.dumps, ensure_ascii=False, default=self.converter)
        loads = loads or json.loads
        super().__init__(dumps, loads)
