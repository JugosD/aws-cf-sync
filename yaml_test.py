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

def up_to(scope, part):
    """ resolve dependencies in direct order """
    parts = [scope[part]]
    try:
        while True:
            required = parts[0][0][KEY_REQUIRE]
            parts.insert(0, [scope[required]])
            del parts[0][0]
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

def build_map(scope):
    """ build ascend and descend maps """
    def get_req(stacks):
        """ get batch dependencies """
        try:
            return stacks[0][KEY_REQUIRE]
        except TypeError:
            return None
    descend_map = {batch:get_req(stacks) for batch, stacks in scope.items()}
    ascend_map = {}
    for batch, require in descend_map.items():
        ascend_map[require] = ascend_map.get(require, []) + [batch]
    print(descend_map)
    print(ascend_map)

def down_to(scope, to):
    """ resolve dependencies in reverse order """
    bindings = {}
    for part, content in scope.items():
        try:
            depend_on = content[0][KEY_REQUIRE]
            bindings[depend_on] = bindings.get(depend_on, []) + [part]
            del content[0]
        except:
            pass
    print(bindings)
    print(bindings[to])
    expand = [[to]]
    go_on = True
    while go_on:
        go_on = False
        for item in expand[0]:
            try:
                expand.insert(0, bindings[item])
                go_on = True
            except KeyError:
                pass
    print(expand)
    # expand = [[stack for stack, req in requirments.items() if req == to])],]
    # while True:
    #     expand[0]

if __name__ == "__main__":
    full_scope = yaml.load(open("test.yaml").read())
    build_map(full_scope)
    #down_to(full_scope, "nat")
    # for stack in list(up_to(full_scope, "log")):
    #     print(stack)