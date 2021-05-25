import logging
import os
import time
from importlib import import_module
from pathlib import Path

import autologging
from prometheus_client import Info, start_http_server
import yaml

from util import Prom

log_level = os.environ.get('SANTABPF_LOG_LEVEL', 'INFO')
log_level = {'TRACE': autologging.TRACE, 'DEBUG': logging.DEBUG, 'INFO': logging.INFO}[log_level]

logging.basicConfig(format='%(filename)s %(funcName)s %(asctime)s %(levelname)-8s %(message)s', level=log_level,
                    datefmt='%m/%d/%Y %I:%M:%S %p')

BASE_PATH = 'scenarios.passive'

if __name__ == '__main__':
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)

    passive_scenarios = {}

    for f in Path.cwd().glob(f'{BASE_PATH.replace(".", "/")}/{config["scenarios"]}.py'):
        module = f'{BASE_PATH}.{f.stem}'
        cls = ''.join(t.title() for t in f.stem.split('_'))

        if config['param']:
            param = config['param'].get(f.stem, None)
        else:
            param = None

        passive_scenarios[f.stem] = getattr(import_module(module), cls)(param=param)

    logging.info(f'{", ".join(passive_scenarios.keys())} loaded...')

    start_http_server(config.get('export_port', 40080))
    elf_report = Info('elf_report', 'the detailed report for troubleshooting from elf')

    while True:
        for name, scenario in passive_scenarios.items():
            logging.info(f'{name} start')
            if scenario.check():
                logging.info(f'{name} triggered')
                elf_report.info(scenario.troubleshoot())
            logging.info(f'{name} end')

            Prom.query.cache_clear()

        time.sleep(config['core']['monitor_interval_sec'])
