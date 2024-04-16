"""
Reliqua Framework.

Copyright 2016-2024.
"""

import inspect
import re

PARAM_REGEX = re.compile(
    r":param\s+(?P<datatype>[\[\]|\w]+)\s+(?P<name>[\S+]+):\s+(\[(?P<options>.*)\])?\s+(?P<description>.*)"
)
PARAM_ITER_REGEX = re.compile(
    r"^(:param.*?:.*?)(?:(?=:param)|(?=:return)|(?=:response)|(?=:accepts))",
    re.MULTILINE | re.DOTALL,
)
RESPONSE_ITER_REGEX = re.compile(r":response\s+(?P<code>\d+)\s*(?P<schema>\w+)?:\s+(?P<description>\w+)")
RETURN_REGEX = re.compile(r"return\s+(\w+):|:return:\s+(\w+)")
ACCEPT_REGEX = re.compile(r"accepts\s+(\w+):|:accepts:\s+(\w+)")
KEYVALUE_REGEX = re.compile(r"(?P<key>\w+)=(?P<value>\w+)")
OPERATION_REGEX = re.compile(r"on_(delete|get|patch|post|put)")
SUFFIX_REGEX = re.compile(r"on_(?:delete|get|patch|post|put)_([a-zA-Z0-9_]+)")


class SphinxParser:
    """
    Sphinx docstring parser.

    This class contains methods to parse resource's method docstring and create
    a structures schema.
    """

    def __init__(self):
        """
        Create SphinxParser instance.

        Create a SphinxParser instance to parse resource doc strings.
        """
        self.doc = ""

    @staticmethod
    def parse_options(string):
        """
        Parse options docstring.

        Parse option information from the docstring.

        :param str string:    Docstring
        :return dict:         Options dict
        """
        options = {
            "location": "query",
            "enum": [],
            "required": False,
            "default": None,
            "min": None,
            "max": None,
        }

        for match in KEYVALUE_REGEX.finditer(string):
            items = match.groupdict()
            options[items["key"]] = items["value"]

        # rename in to location
        options["location"] = options.pop("in")
        options["required"] = True if "required" in string and "optional" not in string else False
        print(options)

        return options

    def parse_parameter(self, string):
        """
        Parse parameter docstring.

        Parse the parameter information from the docstring.

        :param str string:     Docstring
        :return dict:          Parameter dict
        """
        match = PARAM_REGEX.search(string)

        if not match:
            return None

        parameter = match.groupdict()
        if options := parameter.pop("options"):
            parameter.update(self.parse_options(options))

        # set required default based on type
        if not parameter.get("required"):
            parameter["required"] = False

        parameter["description"] = parameter["description"].strip()

        return parameter

    @property
    def summary(self):
        """Return summary."""
        if match := re.search(r"(.*?)\n", self.doc, re.MULTILINE | re.DOTALL):
            return match.group(1).replace("\n", " ").strip()

        return ""

    @property
    def description(self):
        """Return description."""
        if match := re.search(r"\n\n(.*?):", self.doc, re.MULTILINE | re.DOTALL):
            return match.group(1).replace("\n", " ").strip()

        return ""

    @property
    def parameters(self):
        """Return parameters."""
        _parameters = []

        for item in PARAM_ITER_REGEX.finditer(self.doc):
            string = " ".join([x.strip() for x in item.group(1).splitlines()])
            parameter = self.parse_parameter(string)
            if parameter:
                _parameters.append(parameter)

        return _parameters

    @property
    def accepts(self):
        """Return accepts type."""
        if match := ACCEPT_REGEX.search(self.doc):
            return match.group(1) or match.group(2)

        return ""

    @property
    def responses(self):
        """Return responses."""
        _responses = []

        for item in RESPONSE_ITER_REGEX.finditer(self.doc):
            response = item.groupdict()
            response["schema"] = response.get("schema", {})
            _responses.append(response)

        return _responses

    @property
    def content(self):
        """Return content."""
        if match := RETURN_REGEX.search(self.doc):
            return match.group(1) or match.group(2)

        return "json"

    @staticmethod
    def generate_operation_id(method):
        """
        Generate operation id.

        Generate an operation id from the method name.

        :param method method:    Python method
        :return str:             Operation id
        """
        return method.__qualname__

    @staticmethod
    def parse_operation(method):
        """
        Parse operation.

        Parse the operation information from the docstring.

        :param method method:    Python method
        :return dict:            Dict of parameter options
        """
        m = re.search(OPERATION_REGEX, method.__qualname__)
        if m:
            return m.group(1)

        return None

    @staticmethod
    def _parse_suffix(method):
        m = re.search(SUFFIX_REGEX, method.__qualname__)
        if m:
            return m.group(1)

        return None

    def parse(self, method, operation=None, operation_id=None):
        """
        Parse the methods docstring.

        :param method method:     Method with docstring
        :param str operation:     Operation type (default is to parse from method name)
        :param str operation_id:  Operation id (default is to parse from method name)
        :return dict:             Return operation dictionary
        """
        self.doc = inspect.cleandoc(method.__doc__)
        operation = operation or self.parse_operation(method)
        operation_id = operation_id or self.generate_operation_id(method)
        suffix = self._parse_suffix(method)

        return {
            "operation": operation,
            "operation_id": operation_id,
            "suffix": suffix,
            "summary": self.summary,
            "description": self.description,
            "parameters": self.parameters,
            "responses": self.responses,
            "return_type": self.content,
            "accepts": self.accepts,
        }
