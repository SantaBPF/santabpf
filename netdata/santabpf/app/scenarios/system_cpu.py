from loguru import logger

from base import Event, BtRows
from send import send_email
from utils import flamegraph

@logger.catch
def _1min_cpu_usage(event: Event):
    profile = BtRows.from_bpftrace(
        program='profile:hz:99 { @[pid, comm] = count(); }',
        headers=['pid', 'comm', 'count'],
        pattern=r'\[(.+?), (.+?)\]: (.+?)\n',
        types=[int, str, int],
        timeout=3
    )

    svg_id = flamegraph.save_svg(5)
    logger.debug(f'svg_id: {svg_id}')

    msg = (
        f'최근 1분간 cpu 사용량이 비정상적으로 높아짐. 다음은 3초간 샘플링한 (pid, comm)당 on-cpu count\n\n{profile}\n\n'
        f'flamegraph_id: {svg_id}'
    )

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
