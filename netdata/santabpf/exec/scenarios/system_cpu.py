import sys

from base import Event, exec_bpftrace
from send import send_email

def _1min_cpu_usage(event: Event):
    msg = exec_bpftrace('profile:hz:99 { @[pid, comm] = count(); }', ['pid', 'comm', 'count'], '@\[(.+?), (.+?)\]: (.+?)$', 3)
    send_email('dongho971220@gmail.com', repr(event), msg)

def _1min_steal_cpu(event: Event):
    msg = exec_bpftrace('profile:hz:99 { @[pid, comm] = count(); }', ['pid', 'comm', 'count'], '@\[(.+?), (.+?)\]: (.+?)$', 3)
    send_email('dongho971220@gmail.com', repr(event), msg)
