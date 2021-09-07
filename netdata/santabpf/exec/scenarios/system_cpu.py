from base import Event, exec_bpftrace
from send import send_email


def _1min_cpu_usage(event: Event):
    profile = exec_bpftrace(
        program='profile:hz:99 { @[pid, comm] = count(); }',
        headers=['pid', 'comm', 'count'],
        pattern=r'\[(.+?), (.+?)\]: (.+?)\n',
        types=[int, str, int],
        timeout=3
    )

    pids = profile.query('count', lambda _: _ > profile.avg('count') * 2)['pid']
    pred = '||'.join(f'pid=={pid}' for pid in set(pids))
    kstack = exec_bpftrace(
        program=f'profile:hz:99 /{pred}/ {{ @[kstack()] = count(); }}',
        headers=['kstack', 'count'],
        pattern=r'\[([^\[\]]+?)\]: (.+?)\n',
        types=[str, int],
        timeout=5
    )

    msg = f'최근 1분간 cpu 사용량이 비정상적으로 높아짐. 다음은 3초간 샘플링한 (pid, comm)당 on-cpu count\n\n{profile}\n\n{kstack}'

    send_email('dongho971220@gmail.com', repr(event), msg)


def _1min_steal_cpu(event: Event):
    profile = exec_bpftrace(
        program='profile:hz:99 { @[pid, comm] = count(); }',
        headers=['pid', 'comm', 'count'],
        pattern='\[(.+?), (.+?)\]: (.+?)$',
        types=[int, str, int],
        timeout=3
    )

    msg = f'TODO\n\n{profile}'

    send_email('dongho971220@gmail.com', repr(event), msg)
