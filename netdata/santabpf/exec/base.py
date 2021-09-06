#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime
from typing import List, Any
import subprocess
import re
import sys

from tabulate import tabulate

@dataclass
class Event:
    file: str
    roles: str               # the roles that should be notified for this event
    args_host: str           # the host generated this event
    unique_id: str           # the unique id of this event
    alarm_id: str            # the unique id of the alarm that generated this event
    event_id: str            # the incremental id of the event, for this alarm id
    when: str                # the timestamp this event occurred
    name: str                # the name of the alarm, as given in netdata health.d entries
    chart: str               # the name of the chart (type.id)
    family: str              # the family of the chart
    status: str              # the current status : REMOVED, UNINITIALIZED, UNDEFINED, CLEAR, WARNING, CRITICAL
    old_status: str          # the previous status: REMOVED, UNINITIALIZED, UNDEFINED, CLEAR, WARNING, CRITICAL
    value: str               # the current value of the alarm
    old_value: str           # the previous value of the alarm
    src: str                 # the line number and file the alarm has been configured
    duration: str            # the duration in seconds of the previous alarm state
    non_clear_duration: str  # the total duration in seconds this is/was non-clear
    units: str               # the units of the value
    info: str                # a short description of the alarm
    value_string: str        # friendly value (with units)

    def __repr__(self):
        return f'<{self.name}[{self.status}] {self.old_value}->{self.value} {self.when:%X}>'
    
def parse_argv(argv: List[str]) -> Event:
    event = Event(*argv[:20])
    
    event.unique_id = int(event.unique_id)
    event.alarm_id = int(event.alarm_id)
    event.event_id = int(event.event_id)
    
    event.when = datetime.fromtimestamp(int(event.when))
    
    event.value = float(event.value)
    event.old_value = float(event.old_value)
    
    event.duration = float(event.duration)
    event.non_clear_duration = float(event.non_clear_duration)
    
    return event



@dataclass
class BtRow:
    headers: List[str]
    values: List[Any]

    def __repr__(self):
        return f'<{" ".join(f"{k}={v}" for k, v in zip(self.headers, self.values))}>'
    
    def __iter__(self):
        return iter(self.values)
    
@dataclass
class BtRows:
    rows: List[BtRow]
    
    def __post_init__(self):
        # assert len(set(_.name for _ in self.rows)) == 1
        pass
    
    def __repr__(self):
        return tabulate(self.rows, headers=self.rows[0].headers)


def exec_bpftrace(program, headers, pattern, timeout):
    args = ['sudo', 'bpftrace', '-e', f"{program} interval:s:{timeout} {{ exit() }}"]
    print(f'[!] args: {repr(args)}', file=sys.stderr)

    lines = subprocess.check_output(args).decode().splitlines()[4:-1]
    print(f'[!] lines: {repr(lines)}', file=sys.stderr)

    parsed_lines = [re.search(pattern, _).groups() for _ in lines]

    rows = [BtRow(headers, groups) for groups in parsed_lines]

    return str(BtRows(rows))
