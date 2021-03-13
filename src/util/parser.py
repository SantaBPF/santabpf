from functools import cached_property


class Metric:
    def __init__(self, prom_json):
        for key, item in prom_json['metric'].items():
            setattr(self, key, item)

        self.ticks, self.values = zip(*prom_json['values'])
        self.values = list(map(lambda v: round(float(v), 2), self.values))

        self.name = f'{self.chart}-{self.dimension}-{self.family}-{self.instance}-{self.job}'

    @cached_property
    def n(self):
        return len(self.ticks)

    @cached_property
    def sum(self):
        return sum(self.values)

    @cached_property
    def max(self):
        return max(self.values)

    @cached_property
    def min(self):
        return min(self.values)

    @cached_property
    def avg(self):
        return round(self.sum / self.n, 2)

    def __repr__(self):
        return f'{{{self.name}: {self.values}}}'
