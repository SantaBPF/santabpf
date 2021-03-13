import logging

from scenarios._base import Scenario
from util import prom, validator


class InsufficientPageCache(Scenario):
    default_param = {
        'disk_util_weights': [0.75, 0.2, 0.05],
        'page_cache_hit_ratio_threshold': 70
    }

    def validate(self):
        validator.set_default_param(self.param, self.default_param)

    def monitor(self):
        query_ = 'avg_over_time(netdata_disk_util___of_time_working_average[3m])'
        disk_util_3m = prom.query(query_, '3m') or 110
        disk_util_1d = prom.query(query_, '30m', offset='1d') or 110
        disk_util_1w = prom.query(query_, '1h', offset='1w') or 110

        avg_disk_util = sum(
            i[0] * i[1] for i in zip(self.param['disk_util_weights'], (disk_util_3m, disk_util_1d, disk_util_1w)))

        cur_disk_util = prom.query('avg_over_time(netdata_disk_util___of_time_working_average[5m])', '5m')

        logging.debug(f'{disk_util_3m} {disk_util_1d} {disk_util_1w} {avg_disk_util} {cur_disk_util}')

        if cur_disk_util > avg_disk_util:
            self.troubleshoot()

    def troubleshoot(self):
        pass
