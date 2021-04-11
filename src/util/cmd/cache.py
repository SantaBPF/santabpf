from ._base import run as _run


def cachestat(interval=1, count=1):
    return _run(f'cachestat {interval} {count}',
                r'(\d+) (\d+) (\d+) (\d+\.\d+)% (\d+) (\d+)',
                ['hits', 'misses', 'dirties', 'hitratio', 'buffers_mb', 'cached_mb'])
