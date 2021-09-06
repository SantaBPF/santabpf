#!/usr/bin/env python3

import sys

from base import parse_argv
import scenarios

def route(argv):
    event = parse_argv(argv)

    target = getattr(scenarios, f'_{event.name}', None)
    if target is None:
        return

    target(event)


route(sys.argv)
