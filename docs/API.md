https://registry.my-netdata.io/swagger/#/ 를 참고

대략적인 사용법은 아래와 같다.


![image](https://user-images.githubusercontent.com/19762154/131267547-18f2b6ee-c33f-4ccc-b533-12823f7f44fa.png)

1. 서버와 문서의 api 버전이 일치하는지 확인. 현재는 api 버전이 1밖에 없으므로 비교할게 없다.
2. 사용가능한 api들을 확인
3. 한번 어떤 알람들이 사용가능한지 조회하는 api를 사용해보자.
4. alarm 관련으로 찾아보니 /alaram_variables, /alarms, /alarm_values 등등이 보인다.
5. 여기서는 /alarms이 제일 적절해보인다.
6. /alarms 파란 탭을 누르면 다음과 같은 화면을 볼 수 있다.

![image](https://user-images.githubusercontent.com/19762154/131267595-babf164d-e863-4063-92e0-41bdd29e1c05.png)

7. /alarms api는 GET METHOD이고 두 인자를 받는것을 알 수 있다.
8. 여기서는 기본값 그대로 Execute하면 다음과 같은 화면을 볼 수 있다.

![image](https://user-images.githubusercontent.com/19762154/131267615-ea1f13b0-534b-4300-ac5d-08b7be0290f3.png)

9. 여기서 적당히 걸러서 이해해야 한다. Request URL에서 볼 수 있듯이 .../api/v1/alarms 와 같이 요청하면, 아래 response body처럼
알람 관련 정보들이 json 포맷으로 나오는것을 볼 수 있다.
10. 2021/08/30 기준 개발 환경에선 ...이 http://3.34.29.236:29999/host/host-1 이 될것이다.



http://3.34.29.236:29999/host/host-1/api/v1/alarms 
여기서 현재 어떤 알람들이 있는지 확인할 수 있다.

