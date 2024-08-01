"""
Reliqua Framework.

Copyright 2016-2024.
"""

from reliqua.resources.base import Resource


class Docs(Resource):
    """
    Documents endpoint class.

    This class will process resource method doc strings to generate a schema
    that will be used for the API, parameter checking and validation.

    Example:

    Description of method.

    :param str username:  [in_path, required] User ID
    :param str email:     [in_query] User Email
    :param str phone:     [in_query, enum=phones] Phone Numbers

    :response 200:        user was retrieved
    :response 400:        invalid query parameter

    :return json:

    -- Parameters --
    Parameters follow standard Python type. Modifier options are
    placed within []'s and are followed by the parameter description.

    Modifiers are only needed to override default values:

    in_query|in_path|in_body      Where parameter will be read from. [default: in_query]
    required                      Whether parameter is required. [default: False (except POST)]
    enum                          The parameter values are limited by a list.
                                  The enum values will be retrieved from the resource as follows:
                                      if in the form enum=<name>, then name
                                      plural version of parameter name
                                      singular version of the parameter name
    -- Responses --
    By default all standard HTTP messages will be available as defined by status codes. They only
    need to be listed here to change the message or to explicitly show the message in the API
    documentation.

    -- Return --
    The return type of the method.
    """

    no_auth = True

    def __init__(self, schema):
        """
        Create Docs instance.

        :param dict schema:    Documents JSON schema
        :return:               None
        """
        self.schema = schema

    def on_get(self, _req, resp):
        """
        Return the JSON document schema.

        :param Response response:    Response object
        :return:                     None
        """
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.media = self.schema
