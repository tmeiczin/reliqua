import inspect
import re


PARAM_REGEX = re.compile(
    r":param\s+(?P<kind>[|\w]+)\s+(?P<name>[\S+]+):\s+(\[(?P<options>.*)\])?\s+(?P<description>.*)"
)
PARAM_ITER_REGEX = re.compile(
    r"^(:param.*?:.*?)(?:(?=:param)|(?=:return)|(?=:response)|(?=:accepts))",
    re.MULTILINE | re.DOTALL,
)
RESPONSE_ITER_REGEX = re.compile(r":response\s+(?P<code>\d+)\s*(?P<content>\w+)?:\s+(?P<description>\w+)")
RETURN_REGEX = re.compile(r"return\s+(\w+):|:return:\s+(\w+)")
ACCEPT_REGEX = re.compile(r"accepts\s+(\w+):|:accepts:\s+(\w+)")
OPTION_REGEX = {
    "location": r"in_(?P<location>\w+)",
}
KEYVALUE_REGEX = re.compile(r"(?P<key>\w+)=(?P<value>\w+)")
OPERATION_REGEX  = re.compile(r"on_(delete|get|patch|post|put)")


class SphinxParser:

    def __init__(self):
        self.doc = ''

    @staticmethod
    def parse_options(string):
        options = {
            'location': None,
            'enum': [],
            'required': False,
        }

        for option, regex in OPTION_REGEX.items():
            if match := re.search(regex, string):
                options[option] = match.group(1)

        for match in KEYVALUE_REGEX.finditer(string):
            items = match.groupdict()
            options[items["key"]] = items["value"]

        options["required"] = (
            True if "required" in string and "optional" not in string else False
        )

        return options

    def parse_parameter(self, string):
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
        if match := re.search(r"(.*?)\n", self.doc, re.MULTILINE | re.DOTALL):
            return match.group(1).replace("\n", " ").strip()

        return ""

    @property
    def description(self):
        if match := re.search(r"\n\n(.*?):", self.doc, re.MULTILINE | re.DOTALL):
            return match.group(1).replace("\n", " ").strip()

        return ""

    @property
    def parameters(self):
        _parameters = []

        for item in PARAM_ITER_REGEX.finditer(self.doc):
            string = " ".join([x.strip() for x in item.group(1).splitlines()])
            parameter = self.parse_parameter(string)
            if parameter:
                _parameters.append(parameter)

        return _parameters

    @property
    def accepts(self):
        if match := ACCEPT_REGEX.search(self.doc):
            return match.group(1) or match.group(2)

    @property
    def responses(self):
        _responses = [] 
        default_type = 'json' 

        for item in RESPONSE_ITER_REGEX.finditer(self.doc):
            response = item.groupdict()
            response['content'] = response.get('content') or default_type
            _responses.append(response)

        return _responses

    @property
    def content(self):
        if match := RETURN_REGEX.search(self.doc):
            return match.group(1) or match.group(2)

        return "json"

    @staticmethod
    def generate_operation_id(method):
       return method.__qualname__

    @staticmethod
    def parse_operation(method):
       m = re.search(OPERATION_REGEX, method.__qualname__)
       if m:
           return m.group(1)

       return None

    def parse(self, method, operation=None, operation_id=None):
        self.doc = inspect.cleandoc(method.__doc__)
        operation = operation or self.parse_operation(method)
        operation_id = operation_id or self.generate_operation_id(method) 

        return {
            'operation': operation, 
            'operation_id': operation_id,
            'summary': self.summary,
            'description': self.description,
            'parameters': self.parameters,
            'responses': self.responses,
            'return_type': self.content,
            'accepts': self.accepts,
        }
