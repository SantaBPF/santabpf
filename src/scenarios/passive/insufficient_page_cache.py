import logging
from statistics import mean

from autologging import traced

from scenarios._base import Scenario
from util import Prom, cmd


@traced
class InsufficientPageCache(Scenario):
    def check(self):
        if Prom.query('avg_over_time(netdata_disk_util___of_time_working_average[5s]) > 90', '3m'):
            return True
        return False

    def troubleshoot(self):
        return {'name': 'insufficient_pagecache', 'description': '페이지캐시가 부족한 경우 발생하는 시나리오',
                'report': 'test'
                }
