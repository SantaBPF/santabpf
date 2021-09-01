# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Put your name here (your github login)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from bases.FrameworkServices.SimpleService import SimpleService

#priority = 90000

ORDER = [
    'temp_memory',
]

CHARTS = {
    'temp_memory': {
        'options': [None, 'temp_memory', 'MB', 'random', 'random', 'line'],
        'lines': [
            ['TempMemory']
        ]
    }
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.json_path = self.configuration.get('json_path', '/tmp/memcached.json')

    @staticmethod
    def check():
        return True

    def get_data(self):
        data = dict()
        try:
            with open(self.json_path) as f:
                data = json.load(f)
        except Exception as error:
            self.error(error)
            return None
        self.debug('collected data: {}'.format(data))
        return data or None