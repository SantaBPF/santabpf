import logging
import time
from importlib import import_module
from pathlib import Path

import yaml

from util import prom

logging.basicConfig(format='%(filename)s %(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG,
                    datefmt='%m/%d/%Y %I:%M:%S %p')

BASE_PATH = 'scenarios.passive'

if __name__ == '__main__':
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)

    passive_scenarios = {}

    for f in Path.cwd().glob(f'{BASE_PATH.replace(".", "/")}/{config["scenarios"]}.py'):
        module = f'{BASE_PATH}.{f.stem}'
        cls = ''.join(t.title() for t in f.stem.split('_'))

        param = config['param'].get(f.stem, None)

        passive_scenarios[f.stem] = getattr(import_module(module), cls)(param=param)

    logging.info(f'{", ".join(passive_scenarios.keys())} loaded...')

    while True:
        for name, scenario in passive_scenarios.items():
            logging.info(f'{name} start')
            if scenario.monitor():
                scenario.troubleshoot()
            logging.info(f'{name} end')

            prom.query.cache_clear()

        time.sleep(config['core']['monitor_interval_sec'])
