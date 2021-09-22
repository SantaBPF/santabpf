import inspect
import subprocess
from datetime import datetime

import config


def get_svg(timeout, hz):
    svg = subprocess.check_output(
        [
            'sudo', 'sh', '-c',
            f'cd $(dirname {__file__}) && '
            f'perf record -F {hz} -a -g -o- -- sleep {timeout} | '
            f'perf script -i- | ./stackcollapse-perf.pl | ./flamegraph.pl'
        ]
    ).decode()
    return svg


def save_svg(timeout, hz=99) -> str:
    caller = inspect.stack()[1].function
    id = f'{caller}_{datetime.now().strftime("%y%m%d-%H%M%S")}'
    with open(config.SVG_PATH / id, 'w') as f:
        f.write(get_svg(timeout, hz))
    return id
