import logging
from statistics import mean

from autologging import traced

from scenarios._base import Scenario
from util import _prom, cmd


@traced
class InsufficientPageCache(Scenario):
    def check(self):
        if _prom.query('avg_over_time(netdata_disk_util___of_time_working_average[5s]) > 90', '3m'):
            return True
        return False

    def troubleshoot(self):
        cachestat = cmd.cachestat('cachestat 1 3')
        logging.info(mean(cachestat['HITRATIO']))