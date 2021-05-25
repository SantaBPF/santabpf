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
        cachestat = cmd.cachestat(1, 3)
        
        logging.info(mean(cachestat['hitratio']))
        return {'status': 'performance_degradation', 'resource': 'memory',
                'description': 'due to lack of available memory, the page cache size is not enough to process current workload',
                'cachestat': str(cachestat)
                }
