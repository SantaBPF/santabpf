## 개요

Netdata의 Alarm(이하 알람)은 노드들의 anomaly나 퍼포먼스 저하를 조기에 탐지하고 대응할 수 있도록 설계되었다.
Netdata Cloud를 사용한다면 War Room 피쳐들을 활용해볼 수 있겠지만 그렇지 못한 지금 환경에서는 이를 어떻게 다뤄볼 수 있을지 알아본다.

## 설정
알람은 따로 구현할수도 있지만, metric을 생성하는 collector와 해당 metric을 가지고 정상/비정상을 판별하는 알람은 서로 역할을 분리하는것이 좋다.
<sup>[1](#myfootnote1)</sup>

알람을 사용하려면 먼저 Health monitoring이 활성화 되야 하는데 이는 netdata.conf의 [health] 섹션에서 설정할 수 있다.
그리고 각각의 알람은 health.d/ 아래 .conf 파일을 통해 어떤 metric과 collector로부터 어떻게 계산해서 비정상을 탐지할것인지 설정할 수 있다.

즉 알람은 따로 구현이랄게 없고, Health entity라는 파일들을 통해 설정되는 것이다.

## Health entity

#### Entity types
- alarams: 특정 chart와 연결되고 `alarm` 레이블을 사용.
- templates: 특정 context의 모든 chart에 적용되는 규칙을 정의하고 `templaet` 레이블을 사용. 하나의 entity를 모든 디스크들, 모든 네트워크 인터페이스들
과 같은곳에 적용하기에 좋다.

#### Entity format
- `alarm` 또는 `template` line은 맨 위에 있어야 한다.
- `on` line은 항상 필요하다.
- `every` line은 `lookup` 이 없으면 필요하다.
- 모든 entity는 반드시 이들 중 하나를 가진다: `lookup`, `calc`, `warn`, `crit`.

각 line의 개요는 아래를 참고

| line           | required        | functionality                                                                        |
|----------------|-----------------|--------------------------------------------------------------------------------------|
| alarm/template | yes             | Name of the alarm/template.                                                          |
| on             | yes             | The chart this alarm should attach to.                                               |
| class          | no              | The general alarm classification.                                                    |
| type           | no              | What area of the system the alarm monitors.                                          |
| component      | no              | Specific component of the type of the alarm.                                         |
| os             | no              | Which operating systems to run this chart.                                           |
| hosts          | no              | Which hostnames will run this alarm.                                                 |
| plugin         | no              | Restrict an alarm or template to only a certain plugin.                              |
| module         | no              | Restrict an alarm or template to only a certain module.                              |
| charts         | no              | Restrict an alarm or template to only certain charts.                                |
| families       | no              | Restrict a template to only certain families.                                        |
| lookup         | yes             | The database lookup to find and process metrics for the chart specified through on.  |
| calc           | yes (see above) | A calculation to apply to the value found via lookup or another variable.            |
| every          | no              | The frequency of the alarm.                                                          |
| green/red      | no              | Set the green and red thresholds of a chart.                                         |
| warn/crit      | yes (see above) | Expressions evaluating to true or false, and when true, will trigger the alarm.      |
| to             | no              | A list of roles to send notifications to.                                            |
| exec           | no              | The script to execute when the alarm changes status.                                 |
| delay          | no              | Optional hysteresis settings to prevent floods of notifications.                     |
| repeat         | no              | The interval for sending notifications when an alarm is in WARNING or CRITICAL mode. |
| options        | no              | Add an option to not clear alarms.                                                   |
| host labels    | no              | List of labels present on a host.                                                    |

추가적으로 설명이 더 있으면 좋을것 같은 line들은 아래 더 적어놓았다.

#### on
`on: CHART`  
![image](https://user-images.githubusercontent.com/19762154/131266636-433801eb-d416-4da5-bc03-d99bf169988e.png)  
alarm entity의 경우 위와 같이 관심있는 차트의 이름이나 unique id를 사용하면 된다.

`on: CONTEXT`  
![image](https://user-images.githubusercontent.com/19762154/131266651-2f1beb61-b268-4e74-b3a1-1ec1a6b3c8e1.png)  
template entity의 경우 위와 같이 관심있는 context를 사용하면 된다. 위 그림에선 뒤의 disk.io가 context의 이름이다.

#### class
문제 유형을 정의. 기본으로 제공중인 알람들의 class들로는`Errors`, `Latency`, `Utilization`, `Workload`

<a name="myfootnote1">1</a>. 합쳐도 좋은 경우도 있겠지만 여기서는 Netdata의 컨벤션을 따르도록 한다.

#### type, component
크게 해당 알람의 대분류, 소분류를 설정할 수 있다. 각각이 Database, MySQL인 경우 나중에 알람을 Database로 묶고 MySQL로 필터링 하거나 할 수 있다.

#### os, hosts, plugin, module
모두 특정 os, hosts, plugin, module 아래서만 알람이 동작하게 하는 필터 관련 로직이다.

#### lookup
벡터 또는 매트릭스 값인 metric으로 부터 스칼라 값을 계산한다. 즉 이전 10분간의 데이터 100개가 있으면 이를 어떤 임계치와 비교하기 위해선 평균을 내든
최솟값을 찾든 해서 어떤 단일한 값이 필요할 것이다. 여기서 계산된 값은 나중에 `$this` 라는 이름으로 사용할 수 있다.

포맷은 다음과 같다:
`lookup: METHOD AFTER [at BEFORE] [every DURATION] [OPTIONS] [of DIMENSIONS] [foreach DIMENSIONS]`

- METHOD: `average`, `min`, `max`, `sum`, `incremental-sum` 중 하나
- AFTER: -5,-5s -> 이전 5초간, -3m, -7h, -2d -> 이전 3분, 7시간, 2일간의 데이터를 집계
- at BEFORE: 기본 0. AFTER=-7d, BEFORE=-1d 면 이전 7일간 데이터를 전부 보는 대신, 이전 7일부터 이전 1일까지의 데이터만 집계
- every DURATION: lookup의 갱신 주기를 설정
- OPTIONS: `percentage`, `absolute`, `min2max`, `unaligned`, `match-ids`, `match-names` 중 하나.
    - percentage: 값을 반환하는대신, 전체 디멘션 합에 대한 해당 디멘션 합의 비율을 반환. 단위는 %
    - min2max: 여러 디멘션이 주어질때, 이들을 합하는 대신 `max - min`를 반환
    - unaligned: 기본적으로, 데이터가 집계된 경우 (예를 들어 지난 1시간의 데이터 60개가 평균값 1개로 집계된 경우) netdata는 이들을 정렬하여
차트가 항상 일정한 모양이 되도록 한다. (즉 지난 1분에 대한 집계는 항상 XX:XX:00 ~ XX:XX:59 에서만 이뤄진다) unaligned 옵션을 주면 XX:XX:42~XX:XY:42 와 같이 가장 최근의 60초를 집계할 수 있다.
- of/foreach DEMENSIONS: TODO 필요하면 추가함

lookup에서 계산된 결과는 `$this`, `$NAME`으로 사용가능하다.

## calc
lookup 이후에 다른 line에서 사용할 수 있도록 $this를 정제. lookup없이도 alaram_variable을 직접 사용 가능
문법은 https://learn.netdata.cloud/docs/agent/health/reference#expressions 참고

## every
`every: DURATION` 매 `DURATION` 마다 해당 알람을 갱신. `DURATION`은 접미사로 s, m, h, d등을 지원

## green, red
차트의 green, red 임계치를 설정. 둘은 각각 $green, $red로 참조 가능

## warn, crit
warning, critical alram을 언제 트리거할건지 정의. 각각의 표현식은 참/거짓으로 평가될 수 있어야 함

## to
알람이 상태가 변경되었을때 실행될 스크립트의 첫 인자로 넘어가게 될 값. exec line의 기본값은 alarm-notify.sh이다. 따라서 to: admin front 이라 하면 admin과 front role에 알람을 보내게 된다.

## exec
알람이 상태를 변경했을때 실행될 스크립트

## delay
알람이 너무 많이 오는것을 막기 위해 설정할 수 있는 값. 포맷은 다음과 같다:
`delay: [[[up U] [down D] multiplier M] max X]

- `up U`: 알람의 레벨이 올라갔을때 첫 `U DURATION`동안은 알람을 보내지 않는다. 알람이 트리거 되고 금방 다시 원래대로 돌아오는 경우에 유용하다.
- `down D`: `up U`와 맥락은 유사하다. flapping alarm을 방지하는데 유용하다.
- `multiplier M`: 알람이 delayed된 상태일때 상태가 바뀌면 `U`, D`에 `M`을 곱한다.

## repeat
WARNING, CRITICAL 상태일때 알람을 반복해서 보낼건지 설정


# Variables
임의 차트에서 사용되는 변수들을 모두 확인하고 싶다면 `http://NODE/api/v1/alarm_variables?chart=CHART_NAME` 를 사용하면 된다.
netdata에서는 변수들을 위해 3개의 내부 인덱스를 지원한다.
- **chart local variables**: TODO
