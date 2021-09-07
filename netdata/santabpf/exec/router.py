#!/usr/bin/env python3

import sys

from loguru import logger

import scenarios
from base import parse_argv

logger.remove()
logger.add('/var/log/santabpf/log', backtrace=True, diagnose=True, rotation='1 week', compression='gz')


def route(argv):
    event = parse_argv(argv)

    target = getattr(scenarios, f'_{event.name}', None)
    if target is None:
        return

    target(event)


route(sys.argv)
