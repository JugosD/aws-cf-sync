#!/usr/bin/env python
""" yaml test """

from itertools import chain
from collections import namedtuple
import yaml

Stack = namedtuple("stack", ["file_name", "name", "parameters"])

KEY_REQUIRE = "require"
KEY_STACKS = "stacks"
KEY_NAME = "name"
KEY_PARAMETERS = "args"


def scope_pick(scope, part):
    """ get part of scope """
    parts = [scope[part], ]
    try:
        while True:
            required = parts[0][0][KEY_REQUIRE]
            parts[0].pop(0)
            parts = [scope[required]] + parts
    except (KeyError, TypeError):
        pass
    for stack in chain(*parts):
        try:
            stack_file, values = stack.popitem()
            stack_name = values[KEY_NAME]
            parameters = []
            for key, value in values[KEY_PARAMETERS].items():
                parameters.append({
                    "ParameterKey" : key,
                    "ParameterValue": value})
        except AttributeError:
            stack_file = stack
            stack_name = stack
            parameters = []
        except KeyError:
            print("bad_template")
        yield Stack(file_name=stack_file,
                    name=stack_name,
                    parameters=parameters)

if __name__ == "__main__":
    full_scope = yaml.load(open("test.yaml").read())
    print(list(scope_pick(full_scope, "apps")))