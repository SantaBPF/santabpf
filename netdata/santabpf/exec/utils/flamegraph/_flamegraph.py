import subprocess


def get_svg(timeout, hz=99):
    svg = subprocess.check_output(
        [
            'sudo', 'sh', '-c',
            f'cd $(dirname {__file__}) && '
            f'perf record -F {hz} -a -g -o- -- sleep {timeout} | '
            f'perf script -i- | ./stackcollapse-perf.pl | ./flamegraph.pl'
        ]
    ).decode()
    return svg
