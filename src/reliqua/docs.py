def default_responses():
    default_responses = {
        "200": {
            "description": "Successful operation",
        },
        "400": {
            "description": "Bad input values",
        },
    }
    return default_responses


class Docs(object):
    """
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
                                      singlular version of the parameter name
    -- Responses --
    By default all standard HTTP messages will be available as defined by status codes. They only
    need to be listed here to change the message or to explicitly show the message in the API
    documentation.

    -- Return --
    The return type of the method.
    """

    def __init__(self, schema):
        self.schema = schema

    def on_get(self, req, resp):
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.media = self.schema
