import logging

from scenarios._base import Scenario
from util import prom


class InsufficientPageCache(Scenario):
    def monitor(self):
        if prom.query('avg_over_time(netdata_disk_util___of_time_working_average[5s]) > 90', '3m'):
            self.troubleshoot()

    def troubleshoot(self):
        pass
