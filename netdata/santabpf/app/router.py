#!/usr/bin/env python3

import sys

from loguru import logger

import scenarios
from base import parse_argv

import config


@logger.catch
def route(argv):
    event = parse_argv(argv)

    if event.status != 'CRITICAL':
        return

    scenario_name = f'_{event.name}'
    target = getattr(scenarios, scenario_name, None)
    if target is None:
        logger.warning(f"there's no {scenario_name}")
        return

    target(event)


route(sys.argv)
