import json
import logging
import os
import re
import urllib.parse
from datetime import datetime, timedelta

import requests


def _query_with_period(raw_query, start, end, step):
    return json.loads(requests.get(url).content)

def _parse_timedelta_str_to_sec(s):
    assert re.match(r'\d+[smhdw]', s)
    return int(s[:-1]) * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}[s[-1]]

def query(raw_query, duration, step=10):
    host = os.environ['SANTABPF_HOST']
    query_ = urllib.parse.quote_plus(raw_query)

    duration = _parse_timedelta_str_to_sec(duration)
    offset = _parse_timedelta_str_to_sec(offset)

    end = datetime.now() - timedelta(seconds=offset)
    start = end - timedelta(seconds=duration)
    step = step or (duration // 32) + 1

    url = fr'http://{host}/api/v1/query_range?query={query_}&start={start.timestamp()}&end={end.timestamp()}&step={step}'

    return json.loads(requests.get(url).content)['data']['result']
