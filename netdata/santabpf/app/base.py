#!/usr/bin/env python3

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from itertools import compress
from typing import List, Any, Dict, Callable

from loguru import logger
from tabulate import tabulate

@dataclass
class Event:
    file: str
    roles: str  # the roles that should be notified for this event
    args_host: str  # the host generated this event
    unique_id: str  # the unique id of this event
    alarm_id: str  # the unique id of the alarm that generated this event
    event_id: str  # the incremental id of the event, for this alarm id
    when: str  # the timestamp this event occurred
    name: str  # the name of the alarm, as given in netdata health.d entries
    chart: str  # the name of the chart (type.id)
    family: str  # the family of the chart
    status: str  # the current status : REMOVED, UNINITIALIZED, UNDEFINED, CLEAR, WARNING, CRITICAL
    old_status: str  # the previous status: REMOVED, UNINITIALIZED, UNDEFINED, CLEAR, WARNING, CRITICAL
    value: str  # the current value of the alarm
    old_value: str  # the previous value of the alarm
    src: str  # the line number and file the alarm has been configured
    duration: str  # the duration in seconds of the previous alarm state
    non_clear_duration: str  # the total duration in seconds this is/was non-clear
    units: str  # the units of the value
    info: str  # a short description of the alarm
    value_string: str  # friendly value (with units)

    def __repr__(self):
        return f'<{self.name}[{self.status}] {self.old_value}->{self.value} {self.when:%X}>'


@dataclass
class BtRow:
    headers: List[str]
    values: List[Any]
    _types: List[type]

    def __post_init__(self):
        self.values = [t(v) for t, v in zip(self._types, self.values)]

    def __repr__(self):
        return f'<{" ".join(f"{k}={v}" for k, v in zip(self.headers, self.values))}>'

    def __iter__(self):
        return iter(self.values)


@dataclass
class BtRows:
    rows: List[BtRow]

    @classmethod
    def from_str(cls, output, headers, pattern, types):
        groups = re.findall(pattern, output)
        return cls([BtRow(headers, values, types) for values in groups])

    @classmethod
    def from_bpftrace(cls, program, timeout, headers, pattern, types):
        output = bpftrace(program=program, timeout=timeout)
        return cls.from_str(output=output, headers=headers, pattern=pattern, types=types)

    def __post_init__(self):
        self._map: Dict[str, Any] = {header: i for i, header in enumerate(self.rows[0].headers)}

    def __repr__(self):
        return tabulate(self.rows, headers=self.rows[0].headers)

    def __getitem__(self, item):
        return [row.values[self._map[item]] for row in self.rows]

    def top(self, k: str, n: int):
        return BtRows(sorted(self.rows, key=lambda _: _.values[self._map[k]], reverse=True)[:n])

    def avg(self, k: str):
        return sum(self[k]) / len(self[k])

    def query(self, k: str, pred: Callable):
        mask = [pred(_) for _ in self[k]]
        return BtRows(list(compress(self.rows, mask)))


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

    logger.debug(repr(event))
    return event


def bpftrace(*, program, timeout):
    args = ['sudo', 'bpftrace', '-e', f"{program} interval:s:{timeout} {{ exit() }}"]
    logger.debug(f'args: {args}')

    return subprocess.check_output(args).decode()
