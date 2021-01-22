# scenario 2: httpd max clients

Apache HTTP Server라고도 불리는 httpd는 기본적으로 MaxClients 라는 파라미터가 256으로 튜닝되어있다.
모종의 이유로 해당 웹서버에 접속한 클라이언트가 MaxClients 값 이상이 되면 더이상 요청을 처리할 수 없는 것이다.
이렇게 큐 딜레이를 겪게되는 유저는 심각한 latency를 겪게 되고 서비스를 운용하는 관리자 입장에서는 빨리 해결하고 싶은 문제일 것이다.

이러한 문제가 발생하는 이유로는 DoS 공격이 가해졌거나 서버 자체의 설정이 잘못된 경우 또는 크리스마스나 블랙프라이데이처럼 특정한
이벤트로 인해 자연스레 유저들이 몰리게 되는 것들이 있을것이다.

매번 테스트시 마다 Apache HTTP Server 환경을 구축하는 것은 번거로우므로 이를 이미지로 만들고자 했다.

```Dockerfile
FROM httpd:2.4
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./32M /usr/local/apache2/htdocs/
```

httpd는 10억건 이상 pull될 정도로 많이 사용되는 이미지라 Docker Official Images로 관리되고 있다.
여기에 커스터마이징한 설정파일과 테스트용으로 사용할 리소스를 이미지에 같이 넣어준다.

커스텀한 설정으로는 아래와 같다:
```xml
<IfModule mpm_prefork_module>
    StartServers             1
    MinSpareServers          1
    MaxSpareServers          2
    MaxRequestWorkers        5
    MaxConnectionsPerChild   0
</IfModule>
```
기존에는 최대 250개의 요청을 처리할 수 있으나 과정을 단순화 하기 위해 임계치를 5개로 낮추었다.
이럼에도 불구하고 테스트 서버 -> 클라이언트 간 bandwidth가 약 84~93 Mbits/sec이라 32MB 사이즈의 리소스로도 의미 있는 emulating이 되지 않았고
더 큰 사이즈의 리소스를 요청하기보다는 트래픽 비용을 줄이면서 테스트를 할 방법이 필요했다.

