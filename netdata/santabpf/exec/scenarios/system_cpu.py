import sys

from base import Event

def _1min_cpu_usage():
    print('1 MIN CPU USAGE', file=sys.stderr)

def _1min_steal_cpu():
    print('1 MIN STEAL CPU', file=sys.stderr)
