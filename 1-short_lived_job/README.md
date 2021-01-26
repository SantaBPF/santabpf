# scenario 1: short-lived process with top

아래와 같이 짧은 시간동안 cpu resource를 잡아먹고 꺼지는 short-lived process가 주기적으로 실행된다고 해보자.
> systemd에 등록된 서비스가 잘못 설정되어 계속 재시도 되는 경우
서비스 외부에 문제가 있는 상황에서 계속 실패 후 retry하는 경우) 를 가정함

```bash
#!/bin/bash

trap 'kill $(cat /tmp/dd_pid); exit' INT

while :
do
	(dd if=/dev/urandom & echo $! >&3) 3>/tmp/dd_pid | bzip2 -9 >> /dev/null &
	sleep 0.9

	kill $(cat /tmp/dd_pid)
	sleep 2
done
```

interval-sampling 도구인 top(1)에서는 샘플링 주기에 따라 이런 프로세스들이 보이지 않을 수 있다.

아래 top(1)의 결과를 보면 un-niced user의 프로세스들이 전체 CPU 시간의 32%를 잡아먹고 있다고 나오지만
막상 프로세스 목록을 보면 CPU를 점유하고 있는 프로세스가 보이지 않는다.

```sh
top - 02:30:59 up 4 days, 15:29,  3 users,  load average: 0.55, 0.24, 0.09
Tasks: 106 total,   1 running, 105 sleeping,   0 stopped,   0 zombie
%Cpu(s): 32.0 us,  1.7 sy,  0.0 ni, 66.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    978.6 total,    151.4 free,    245.1 used,    582.1 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    568.7 avail Mem 

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                                                                                                                
   5764 mongodb   20   0 1501184  75352  11832 S   0.3   7.5  20:47.32 mongod                                                                                                                 
      1 root      20   0  169072  10892   6296 S   0.0   1.1   0:18.71 systemd                                                                                                                
      2 root      20   0       0      0      0 S   0.0   0.0   0:00.00 kthreadd                                                                                                               
      3 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 rcu_gp                                                                                                                 
      4 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 rcu_par_gp                                                                                                             
      6 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/0:0H-
```
이를 위해 atop(1)을 사용해 볼 수도 있지만 atop(1)의 결과는 너무 장황해서 필요한 정보로 가공하는데 어려움이 있고 
불필요한 정보들까지 같이 처리하여 비교적 오버헤드가 크다.

pidstat(1)도 atop(1)과 비슷한 목적으로 사용가능하지만 파싱하기 더 쉽게 출력된다.

처음부터 우리가 필요한 정보만 추출할 수 있으면 가공하기도 쉽고 오버헤드도 적을텐데 
프로세스 생성을 모니터링하려면 어떻게 해야할까

![image](https://user-images.githubusercontent.com/19762154/104984758-b70f8d80-5a52-11eb-9a11-e1a2eae281a2.png)

OS 수업 내용과 위 그래프를 참고해 exec syscall을 모니터링 해보기로 했다.

exec는 execvp  execv execvpe execle 등등 여러 family가 있는것처럼 보였는데
ausyscall(8)로 확인한 결과 현재 아키텍처에서는 execve만 존재하는걸로 보였다.

먼저 아래와 같이 어떤 exec에 대해 tracepoint가 있는지 확인했다. probe와 비교했을때 tracepoint가 인터페이스면에서 더 안정적이어서 tracepoint를 먼저 찾았다.

```bash
ubuntu@ip-172-31-46-92:~$ sudo bpftrace -lv 't:syscalls:*enter_exec*'
tracepoint:syscalls:sys_enter_execve
    int __syscall_nr;
    const char * filename;
    const char *const * argv;
    const char *const * envp;
...
```

보면 execve syscall이 호출될때(return될때는 exit_exec 사용) 호출되는 tracepoint:syscalls:sys_enter_execve 라는 tracepoint와
제공되는 파라미터들을 확인할 수 있었다.

그래서 아래와 같이 bpftrace로 작은 bpf 프로그램을 만들어 검증해볼 수 있었다.
이를 좀 더 고도화하면 bcc를 사용해 세부적인 정보들을 더 활용해 볼 수 있겠다.

```bash
ubuntu@ip-172-31-46-92:~$ sudo bpftrace -e 't:syscalls:sys_enter_execve { printf("[%d] ", pid); join(args->argv)}'
Attaching 1 probe...
[62130] sh gen-shortlived-jobs.sh
[62133] sleep 0.9
[62132] bzip2 -9
[62134] dd if=/dev/urandom
[62135] cat /tmp/dd_pid
[62136] sleep 2
[62139] sleep 0.9
[62138] bzip2 -9
[62140] dd if=/dev/urandom
[62141] cat /tmp/dd_pid
[62142] sleep 2
[62143] cat /tmp/dd_pid
...
```

distro마다 배포된 bcc 패키지가 다른데 ubuntu의 경우 bpfcc-tools라는 이름으로 배포되고 있다.
위의 기능을 python-bcc로 다시 짠 tool은 execsnoop-bpfcc 라는 이름으로 관리되고 있다.

cli에서 one-liner로 작성되는 대신 코드는 더 길지만 많은 작업을 할 수 있다.

```bash
ubuntu@ip-172-31-46-92:~$ sudo execsnoop-bpfcc -T
TIME     PCOMM            PID    PPID   RET ARGS
03:46:46 sh               62188  61635    0 /usr/bin/sh gen-shortlived-jobs.sh
03:46:46 sleep            62191  62188    0 /usr/bin/sleep 0.9
03:46:46 bzip2            62190  62188    0 /usr/bin/bzip2 -9
03:46:46 dd               62192  1        0 /usr/bin/dd if=/dev/urandom
03:46:47 cat              62193  62188    0 /usr/bin/cat /tmp/dd_pid
03:46:47 sleep            62194  62188    0 /usr/bin/sleep 2
03:46:49 sleep            62197  62188    0 /usr/bin/sleep 0.9
03:46:49 bzip2            62196  62188    0 /usr/bin/bzip2 -9
03:46:49 dd               62198  1        0 /usr/bin/dd if=/dev/urandom
03:46:50 cat              62199  62188    0 /usr/bin/cat /tmp/dd_pid
```

오픈소스므로 다른 정보가 더 필요하다면 직접 수정해도 되고
아니면 다른 도구들과 연계하여 더 깊게 분석해볼 수 있을것 같다.

여기서는 시나리오가 너무 단순해 pidstat과 ppid만 사용해도 될것 같았지만
이런식으로 bpf를 활용해볼수 있다는 것을 보여주고 싶었다.  
