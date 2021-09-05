Netdata에서 사용되는 용어들을 정리했다. 처음엔 모두 한글로 옮겼지만 family 서부터는 의역하거나 음차를 써도 의미가 애매해져 용어는 원문을 그대로 썼다.

자세한 내용은 아래를 참고
https://learn.netdata.cloud/docs/agent/web#charts-contexts-families

## Chart
- Chart는 수집/계산된 메트릭을 보여주는 역할을 한다.
- collector에 의해 생성된다
- 다음은 시스템 CPU Chart다. ![image](https://user-images.githubusercontent.com/19762154/132116535-609f9cfa-2b57-4d6e-9018-cda56873d459.png)
- Chart 위에 (...)에 있는게 Chart의 이름이다. 위의 경우 system.cpu가 해당 Chart의 이름이다.

## Dimension
- Dimension은 Chart에서 보여지는 값이다.
- 값은 비율, 집계와 같이 계산된 값이거나 아니면 raw data가 될 수 있다.
- Chart는 하나 이상의 Dimension을 보여줄 수 있다.
- netdata는 Dimension들을 Chart 우측에 보여주고 있다.
- 다음 시스템 CPU Chart의 Dimension들이다. ![image](https://user-images.githubusercontent.com/19762154/132116651-c92abf4d-7e6b-415d-a035-dafd7c1b1e6c.png)

## Family
- family는 모니터링 되고 있는 하드웨어 또는 소프트웨어가 다른 유사한 것들과 구분될 수 있도록 해준다.
- 예를 들어, 현재 시스템이 여러 디스크 sda, sdb를 가지고 있다 하자, family sda는 sda에 종속된 DB meric, io metric 들을 묶어준다.
- TODO 더 자세한 설명이 필요

## Context
- context는 수집된 metric의 종류와 보여줄 dimension으로 어떻게 차트들을 묶어줄지 결정한다.
- 다른 chart들에 대해 동일한 context는 같은 dimension을 보여주지만 각각의 family 마다 그룹핑 된다.
- 예를 들어 sda, sdb family가 있고 disk.io, disk.util context가 있으면 netdata는 다음 chart들을 생성한다:
`disk_io.sda` `disk_io.sdb` `disk_util.sda` `disk_util.sdb`
- disk.io context에 대한 sdb, sdd family의 예시는 다음과 같다: ![image](https://user-images.githubusercontent.com/19762154/132117257-148d9d10-2fa5-4fba-8821-ede9f6e2f2e1.png)
![image](https://user-images.githubusercontent.com/19762154/132117261-1e37c4ff-b946-40f7-9f1c-08ace4371199.png)
- 이는 alaram template에서도 유용하다. 여러 네트워크 인터페이스가 있는 경우 하나의 템플릿으로 모든 인터페이스를 처리할 수 있다.
