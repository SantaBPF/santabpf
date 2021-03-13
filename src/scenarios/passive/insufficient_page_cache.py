import logging
from statistics import mean

from autologging import traced

from scenarios._base import Scenario
from util import prom, shell


@traced
class InsufficientPageCache(Scenario):
    def monitor(self):
        if prom.query('avg_over_time(netdata_disk_util___of_time_working_average[5s]) > 90', '3m'):
            self.troubleshoot()

    def troubleshoot(self):
        cachestat = shell.run('cachestat 2 5')
        logging.info(mean(cachestat['HITRATIO']))