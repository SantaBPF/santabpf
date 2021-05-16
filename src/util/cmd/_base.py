import re
import subprocess

import pandas as pd


def run(cmd, pattern, headers, *, timeout=None):
    """
    임의의 shell명령을 실행하고 결과를 DataFrame으로 반환
    Args:
        cmd: 실행할 명령
        pattern: parse_output 참고
        headers: parse_output 참고
        timeout: {timeout}초가 넘어가면 TimeoutError 반환

    Returns: DataFrame 타입의 shell command output

    Examples:
        cmd.run('ps', '(\d+) (\w+)', ['pid', 'tty']).head()
        cmd.run('ps', '(\d+) \w+ ([\w:.]+)', ['pid', 'time'])
    """

    return parse_output(raw_run(cmd, timeout=timeout), pattern, headers)


def raw_run(cmd, *, timeout=None):
    return subprocess.check_output(['/bin/sh', '-c', cmd], timeout=timeout, text=True).splitlines()


def parse_output(output, pattern, headers):
    """
    newline으로 구분된 str의 list를 받아 pattern에 해당하는 그룹을 생성하고 headers로 column을 만들어 DataFrame으로 반환
    Args:
        output: newline으로 구분된 str의 list
        pattern: 각 row를 파싱할 정규식
        headers: 헤더로 사용할 문자열의 리스트, None으로 생략 가능, 자동으로 패딩됨

    Returns: 각 row를 pattern의 group들로 하고 column을 headers로 하는 DataFrame
    """

    body = []
    for line in output:
        compacted_line = re.sub(r'\s+', ' ', line).strip()

        match = re.match(pattern, compacted_line)
        if match:
            body.append(match.groups())

    padded_headers = headers + [None] * (len(body[0]) - len(headers))

    df = pd.DataFrame(body, columns=padded_headers)[filter(None, headers)]

    return df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
