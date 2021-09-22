import sys
from pathlib import Path as _Path

from loguru import logger

LOG_PATH = _Path('/var/log/santabpf')
SVG_PATH = _Path('/usr/libexec/netdata/santabpf/svg')

logger.remove()
logger.add(LOG_PATH / 'log_{time:YYMMDD}.log',
           format="{time:YY/MM/DD hh:mm:ss} - {level} - {name}/{function}:{line} - {message}")
logger.add(sys.stdout, format="{time:YY/MM/DD hh:mm:ss} - {level} - {name}/{function}:{line} - {message}")
