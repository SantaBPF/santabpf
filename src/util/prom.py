from datetime import datetime, timedelta
import json
import os
import re
import urllib.parse

import requests

def _query_with_period(raw_query, start, end, step):

    
    return json.loads(requests.get(url).content)

def query(raw_query, duration, step=10):
    host = os.environ['SANTABPF_HOST']
    query = urllib.parse.quote_plus(raw_query)
    
    if re.match(r'\d+[smhdw]', duration):
        duration = int(duration[:-1]) * {'s':1, 'm':60, 'h':3600, 'd':86400, 'w':604800}[duration[-1]]
        end = datetime.now()
        start = end - timedelta(seconds=duration)
    else:
        raise ValueError
    
    url = fr'http://{host}/api/v1/query_range?query={query}&start={start.timestamp()}&end={end.timestamp()}&step={step}'
    
    return json.loads(requests.get(url).content)['data']['result']