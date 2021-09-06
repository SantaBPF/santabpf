import sys

from base import Event, exec_bpftrace
from send import send_email

def _1min_cpu_usage(event: Event):
    send_email('dongho971220@gmail.com', repr(event), str(exec_bpftrace('profile:hz:99 { @[pid, comm] = count(); }', 3)))

def _1min_steal_cpu():
    send_email('dongho971220@gmail.com', repr(event), str(exec_bpftrace('profile:hz:99 { @[pid, comm] = count(); }', 3)))
