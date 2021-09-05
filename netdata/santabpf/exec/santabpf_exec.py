#!/usr/bin/env python3

import sys

from base import parse_argv
import scenarios

def route(argv):
    event = parse_argv(argv)
    print('!!!! event', event, file=sys.stderr)

    target = getattr(scenarios, f'_{event.name}', None)
    if target is None:
        return
    print('!!!! target', target, file=sys.stderr)

    target()
    print('!!!! target called', target, file=sys.stderr)


route(sys.argv)
