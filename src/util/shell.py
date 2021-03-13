import re
import subprocess


def run(cmd, *, timeout=None):
    return _parse_table(_run(cmd, timeout=timeout))


def raw_run(cmd, *, timeout=None):
    return _run(cmd, timeout=timeout)


def _run(cmd, *, timeout=None):
    return subprocess.check_output(['/bin/sh', '-c', cmd], timeout=timeout, text=True,
                                   stderr=subprocess.STDOUT).splitlines()


def _parse_table(output):
    def to_number(x): float(re.sub('[^0-9.]', '', x))

    header = output[0].split()
    body = (map(to_number, o.split()) for o in output[1:])

    return dict(zip(header, zip(*body)))
