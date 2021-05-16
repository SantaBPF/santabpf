from ._base import run


def cachestat(interval=1, count=1):
    return run(f'cachestat {interval} {count}',
               r'(\d+) (\d+) (\d+) (\d+\.\d+)% (\d+) (\d+)',
               ['hits', 'misses', 'dirties', 'hitratio', 'buffers_mb', 'cached_mb'])
