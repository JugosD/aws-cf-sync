#!/usr/bin/env python
""" yaml test """

from itertools import chain
from collections import namedtuple
import logging
import yaml

Stack = namedtuple("stack", ["name", "parameters", "file_name"])

KEY_REQUIRE = "require"
KEY_STACKS = "stacks"
KEY_NAME = "name"
KEY_PARAMETERS = "args"

DIRECTION_ASCEND = "ascend"
DIRECTION_DESCEND = "descend"

def batches_map(config, target=None, direction=DIRECTION_DESCEND):
    """ build ascend and descend maps """

    def resolve_dependencies(resolve, dependency_map):
        """ resolve dependencies """
        while resolve:
            batch = resolve.pop()
            resolve.extend(dependency_map[batch])
            yield batch

    get_requiries = lambda stacks: (stack[KEY_REQUIRE]
                                    for stack in stacks
                                    if KEY_REQUIRE in stack)
    descend = {batch : get_requiries(stacks)
               for batch, stacks in config.items()}

    if direction == DIRECTION_DESCEND:
        dependency_map = descend
        revers_stack = False

    if direction == DIRECTION_ASCEND:
        ascend = {require : [] for require in config.keys()}
        for batch, requires in descend.items():
            for require in requires:
                ascend[require].append(batch)
        dependency_map = ascend
        revers_stack = True

    batches = reversed(list(resolve_dependencies(resolve=[target],
                                                 dependency_map=dependency_map)))
    return chain(*(reversed(config[batch]) if revers_stack else config[batch]
                   for batch in batches))

def get_stacks(config=None, target=None, direction=DIRECTION_DESCEND):
    """ get stacks """
    for stack in batches_map(config, target, direction):
        try:
            stack_file, stack_args = stack.popitem()
            if stack_file == KEY_REQUIRE:
                continue
            try:
                stack_name = stack_args[KEY_NAME]
            except KeyError:
                stack_name = stack_file
            try:
                parameters = stack_args[KEY_PARAMETERS]
            except KeyError:
                parameters = {}
        except (TypeError, AttributeError):
            stack_file = stack
            stack_name = stack
            parameters = {}
        except KeyError:
            logging.error("Config parse error")
            raise KeyError
        yield Stack(file_name=stack_file,
                    name=stack_name,
                    parameters=parameters)