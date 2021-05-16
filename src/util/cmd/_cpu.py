from ._base import run


def cpudist(interval=1, count=1):
    return run(f'cpudist {interval} {count}',
               r'(\d+) -> (\d+) : (\d+) \|(\**)',
               ['usecs_start', 'usecs_end', 'count'])
