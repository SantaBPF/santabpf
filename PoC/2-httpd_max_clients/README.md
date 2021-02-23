# scenario 2: httpd max clients

Apache HTTP Server라고도 불리는 httpd는 기본적으로 MaxClients 라는 파라미터가 256으로 튜닝되어있다.
모종의 이유로 해당 웹서버에 접속한 클라이언트가 MaxClients 값 이상이 되면 더이상 요청을 처리할 수 없는 것이다.
이렇게 queuing delay를 겪게되는 유저는 심각한 latency를 겪게 되고 서비스를 운용하는 관리자 입장에서는 빨리 해결하고 싶은 문제일 것이다.

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

iproute2 패키지에서 같이 제공되는 tc(8)은 리눅스 커널 패킷 스케줄러를 설정할 수 있게 해준다.
그래서 테스트 시에
`sudo tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms`
를 설정해 초당 1Mbit 정도의 속도로만 트래픽이 전송될 수 있도록 했다.

2번째 시나리오를 emulating하기 위한 스크립트는 아래처럼 작성된 run.sh이다:
```bash
#!/bin/bash -x

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# safety logic
trap 'tc qdisc del dev eth0 root; rm 32M; exit' INT

pushd test-httpd

# for generating high load
sh gen_dummy_data.sh 32M
docker build -t 2-httpd_max_clients .

# tc for emulating tcp congestion
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms
docker run -it --rm --name 2-httpd_max_clients -p 5001:80 2-httpd_max_clients
tc qdisc del dev eth0 root
rm ./32M
```

tc(8)를 사용하기 위해 sudo 권한이 필요하다. 실행 시키면 동적으로 이미지가 빌드되고 컨테이너로 띄어지면서 아래와 같이 httpd daemon의 로그 화면이 보일것이다.

![image](https://user-images.githubusercontent.com/19762154/105512603-a857fd80-5d14-11eb-96e0-68ed46f053a5.png)

이제 클라이언트에서 서버로 요청을 날려볼 수 있다. 초당 트래픽을 1Mbit으로 제한을 걸어둔 상태이므로 32MB 크기의 리소스를 요청하면 MaxClients에 도달하기까지 충분한 시간을 확보할 수 있을것이다.

![image](https://user-images.githubusercontent.com/19762154/105518106-359e5080-5d1b-11eb-987a-a7815f2aac77.png)


클라이언트에서 5건의 request를 동시에 보내자 서버에서 MaxRequestWorkers(MaxClients)에 도달했다고 경고하는 것을 볼 수 있다.

여기서 ss(8), lsof(8), netstat(8) 같은 명령어로 상황을 파악하려고 하면 잘 되지 않는다.
호스트 환경과 격리된 컨테이너의 네트워크 문제인것 같은데 이부분은 더 리서치가 필요해 다음 시나리오에서 다뤄야 할 것 같다.

iftop(8)에 -P 옵션을 줘서 보면 src ip와 port까진 나오는데 어떤 pid가 해당 요청을 처리하고 있는지까진 나오지 않는다.
여기서 bpf를 다음과 같이 활용해볼 수 있었다.


![image](https://user-images.githubusercontent.com/19762154/105515499-1a7e1180-5d18-11eb-83f7-f80ccd1b45ca.png)


tcptop(8)는 커널의 tcp_sendmsg와 tcp_recvmsg에 kprobe를 붙여 작동한다. 하지만 이전 sys_enter_execve tracepoint와는 달리 이번에는 아래처럼 처리해야할 로직이 길기 때문에 bpftrace 대신 하위레벨의 bcc로 작성되었다.
```c
...
int kprobe__tcp_sendmsg(struct pt_regs *ctx, struct sock *sk,
    struct msghdr *msg, size_t size)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    ...
    if (family == AF_INET) {
        struct ipv4_key_t ipv4_key = {.pid = pid};
        ipv4_key.saddr = sk->__sk_common.skc_rcv_saddr;
        ipv4_key.daddr = sk->__sk_common.skc_daddr;
        ipv4_key.lport = sk->__sk_common.skc_num;
        dport = sk->__sk_common.skc_dport;
        ipv4_key.dport = ntohs(dport);
        ipv4_send_bytes.increment(ipv4_key, size);

    } else if (family == AF_INET6) {
    ...
```

tcptop(8)의 결과를 보면 10초동안 80번 http 포트에서 xxx.xx.138.101 클라이언트 호스트로 5건의 tcp_sendmsg가 전송되었다는 사실과 누가(pid, comm) 요청을 처리하고 있었는지와 rx/tx 사이즈도 확인할 수 있었다. 

이번에는 요청을 받을 수 있는 최대 5개를 넘어 6건의 요청을 날려봤다.

![image](https://user-images.githubusercontent.com/19762154/105519806-346e2300-5d1d-11eb-9ce5-46618ac0373e.png)
![image](https://user-images.githubusercontent.com/19762154/105520303-df7edc80-5d1d-11eb-8213-8259034e5be3.png)

보면 뒤에온 요청은 아예 처리도 되지 않고 있다는것과 동시에 들어온 요청도 클라이언트마다 큰 차이가 있다는 것이다. 후자의 경우는 실험 환경이 열악해 부득이 호스트 한대에서 포트만 바꿔 여러곳에서 동시 접속하는것을 모방해서 그럴 수 있다고 쳐도 MaxClients 이후의 queuing delay를 겪는 유저의 경우 아예 아무런 응답조차 받고 있지 못하는 것은 큰 문제가 아닐 수 없다. 포트별로 전송속도에 차이가 있는거에 대해서도 실험을 해보고 싶었으나 테스트에 활용된 호스트가 Windows 호스트 안에 Linux VM으로 돌고 있어 이를 추적하기 어려웠다. vmware에서 가상 네트워크 관련 포트 포워딩 설정은 유료버전에서만 지원되기 때문이다.

이번 시나리오에서는 동시에 큰 자원을 여러번 요청해 서비스가 더이상 제대로 운용될 수 없도록 했기 때문에 모의 DoS 공격을 했다고 볼 수 있다.  이런경우 위에서 활용한 tcptop(8)으로 현재 어떤 ip에서 정상적이지 않은 요청을 하고 있는지 확인해보거나

아래와 같이 tcpstates(8)을 활용해 downtime 없이 임계치를 벗어나면 바로 차단해버릴수도 있을것이다. 

![image](https://user-images.githubusercontent.com/19762154/105522225-4e5d3500-5d20-11eb-9ddc-b523610f4882.png)


tcptop(8)과 tcpstates(8) 모두 tracing의 범주의 들어간다. 각각 TCP send/receive event와 TCP set state event를 tracing 하므로 이 tool에 대한 오버헤드는 단위시간당 얼마나 많은 tcp_sendmsg/tcp_recvmsg가 호출되는지, 얼마나 많은 TCP 세션이 생성되는지에 따라 결정된다. 전자는 나중에 살펴볼 다른 bpf tool인 funccount로 직접 해당 커널 함수 호출을 카운팅해보거나 후자는 sar(8)로 `sar -n DEV 1`과 같이 측정해 볼 수 있을것이다. 

미리 벤치마킹된 자료에 의하면 tcptop의 경우 초당 4k ~ 15k건의 이벤트가 발생하는 경우 0.5~2% CPU 오버헤드가 발생했고 1k 미만이라면 무시할만한 수준이라고 한다. tcpstates는 tracing으로 인한 오버헤드보다 결과를 출력하는데 걸리는 시간이 더 커서 고려하지 않아도 될것 같다.
