# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

from bases.FrameworkServices.ExecutableService import ExecutableService

ORDER = [
    'pagecache_count',
]

CHARTS = {
    'pagecache_count': {
        'options': [None, 'Pagecache conut', 'count/sec', 'pagecache', 'pagecache', 'line'],
        'lines': [
            ['hits'],
            ['misses']
        ]
    }
}


class Service(ExecutableService):
    def __init__(self, configuration=None, name=None):
        ExecutableService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.command = ['cachestat', '1', '1']

    @staticmethod
    def check():
        return True

    def get_data(self):
        lines = self._get_raw_data()
        hits, misses = map(int, lines[-1].split()[:2])

        return {'hits': hits, 'misses': misses}
