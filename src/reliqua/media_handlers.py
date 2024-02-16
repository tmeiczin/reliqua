import json
from datetime import date, datetime, time
from functools import partial

import falcon
import yaml
from falcon.media import BaseHandler
from falcon.media import JSONHandler as FalconJSONHandler
from yaml import SafeLoader

from pxops.util import unused


class YAMLHandler(BaseHandler):
    """Media handler class for YAML."""

    def deserialize(self, stream, content_type, content_length):
        """
        Load YAML from stream and return the appropriate Python object.

        :param stream:      stream to load from
        :return:            deserialized YAML as python object
        """
        unused([content_type, content_length])
        try:
            return yaml.load(stream.read().decode("utf-8"), SafeLoader)
        except ValueError as exception:
            raise falcon.HTTPBadRequest(
                title="Invalid YAML",
                description=f"Could not parse YAML body: {exception}",
            ) from exception

    def serialize(self, media, content_type):
        """
        Serialize media to YAML.

        :param media:       media to serialize
        :return:            serialized YAML
        """
        unused([content_type])
        result = yaml.dump(media)

        try:
            result = result.encode("utf-8")
        except AttributeError:
            pass

        return result


class TextHandler(BaseHandler):
    """Media handler class for text."""

    def deserialize(self, stream, content_type, content_length):
        """
        Read text from stream.

        :param stream:      stream to load from
        :return:            text
        """
        unused([content_type, content_length])
        try:
            return stream.read().decode("utf-8")
        except ValueError as exception:
            raise falcon.HTTPBadRequest(
                title="Invalid Text", description=f"Could not parse body: {exception}"
            ) from exception

    def serialize(self, media, content_type):
        """
        Serialize media to text.

        :param media:       media to serialize
        :return:            serialized text
        """
        unused([content_type])
        result = f"{media}"

        try:
            result = result.encode("utf-8")
        except AttributeError:
            print("crap")
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
