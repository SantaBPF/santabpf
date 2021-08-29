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

