import json
import logging
import os
import re
import urllib.parse
from datetime import datetime, timedelta
from functools import cache

import requests

from .parser import Metric


def _parse_timedelta_str_to_sec(s):
    assert re.match(r'\d+[smhdw]', s)
    return int(s[:-1]) * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}[s[-1]]


@cache
def query(raw_query, duration, offset='0s', step=None):
    host = os.environ['SANTABPF_HOST']
    query_ = urllib.parse.quote_plus(raw_query)

    duration = _parse_timedelta_str_to_sec(duration)
    offset = _parse_timedelta_str_to_sec(offset)

    end = datetime.now() - timedelta(seconds=offset)
    start = end - timedelta(seconds=duration)
    step = step or (duration // 32) + 1

    url = fr'http://{host}/api/v1/query_range?query={query_}&start={start.timestamp()}&end={end.timestamp()}&step={step}'

    try:
        content = requests.get(url).content
        obj = json.loads(content)

        logging.debug(obj)
        # return obj
        return [Metric(result) for result in obj['data']['result']]
    except IndexError:
        return None
    except Exception as e:
        logging.warning(repr(obj))
        raise e
