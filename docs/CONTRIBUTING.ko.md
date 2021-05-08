# 1. 개발 환경 구성
## 1. Python 개발 환경 구성
1. `git clone https://github.com/SantaBPF/santabpf`로 레포 복사
2. pyproject.toml을 참고하여 적절한 버전과 환경을 구축. 여기서는 [asdf](https://github.com/asdf-vm/asdf)와 [poetry](https://github.com/python-poetry/poetry)를 활용한다.
```
$ asdf install python 3.9.4
$ poetry env use 3.9.4
$ poetry install
```
3. poetry를 적절히 설치한 경우, 해당 프로젝트 경로에 들어가면 자동으로 전용 가상 환경을 activate할 것 이다. 확실하지 않다면 `poetry env info`로 확인
4. 프로젝트 루트 경로에서 `jupyter notebook`을 해서 브라우저에 Jupyter Notebook 환경이 열리면 성공. 단 (3)이 제대로 되지 않은 경우 이후 문제가 발생할 수 있다.

## 2. BPF 개발 환경 구성<sup>[1](#footnote-bpf)</sup>
BPF는 Linux 4.x 이후 커널에 내장된 기능으로 VM<sup>[2](#footnote-vm)</sup>내에서 임의의 코드를 돌려볼 수 있게 해준다.
임의의 코드를 작성해 커널의 자료구조에 접근할 수 있다는 점, 이를 실행하는데 별도의 커널 재컴파일이나 모듈 작성이 필요없다는 점, 에러 발생 시 kernel-crash로 이어지지 않는다는 점
덕분에 Security, Tracing & Profiling, Networking, Observability & Monitoring와 같은 분야에서 다양하게 활용되고 있다.

BPF 프로그램은 BPF bytecode로 구성된다. 아무리 BPF가 좋다지만 어셈블리 수준과 다름없는 bytecode로 코딩하고 싶은 사람은 없을거다. c로 코딩하면 컴파일러가 어셈블리어로 변환해주는 것과 같이
c나 python 기타 다른 언어로 BPF 프로그램을 작성할 수 있다. 이를 bcc라 하며 관계는 bcc(c, python, ...) -> BPF program가 된다. bcc도 작성하기 번거로운 사람들을 위해 bcc를 한 단계 더 추상화한
bpftrace나 ply같은 것들이 있다. 각 레벨의 코드 예시는 아래와 같다:

#### 1. pure bpf bytecode
```
...
    ld #20
    ldx 4*([0]&0xf)
    add x
    tax

lb_0:
    ; Match: 076578616d706c6503636f6d00 '\x07example\x03com\x00'
    ld [x + 0]
    jneq #0x07657861, lb_1
    ld [x + 4]
    jneq #0x6d706c65, lb_1
    ld [x + 8]
    jneq #0x03636f6d, lb_1
    ldb [x + 12]
    jneq #0x00, lb_1
    ret #1

lb_1:
    ret #0
...
```


#### 2. bcc w/ python
```
...
REQ_WRITE = 1		# from include/linux/blk_types.h

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
BPF_HASH(start, struct request *);
void trace_start(struct pt_regs *ctx, struct request *req) {
	// stash start timestamp by request ptr
	u64 ts = bpf_ktime_get_ns();
	start.update(&req, &ts);
}
void trace_completion(struct pt_regs *ctx, struct request *req) {
	u64 *tsp, delta;
	tsp = start.lookup(&req);
	if (tsp != 0) {
		delta = bpf_ktime_get_ns() - *tsp;
		bpf_trace_printk("%d %x %d\\n", req->__data_len,
		    req->cmd_flags, delta / 1000);
		start.delete(&req);
	}
}
""")

if BPF.get_kprobe_functions(b'blk_start_request'):
        b.attach_kprobe(event="blk_start_request", fn_name="trace_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_start")
b.attach_kprobe(event="blk_account_io_done", fn_name="trace_completion")
...
```

#### 3. bpftrace
```
# Files opened by process
bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s %s\n", comm, str(args->filename)); }'

# Syscall count by program
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'

# Read bytes by process:
bpftrace -e 'tracepoint:syscalls:sys_exit_read /args->ret/ { @[comm] = sum(args->ret); }'

# Read size distribution by process:
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @[comm] = hist(args->ret); }'
```

본 프로젝트의 목적은 bpf 자체를 개발하는것이 아닌 bpf를 잘 활용하여 트러블슈팅을 보조하는 것이므로 가급적 고수준의 스택을 사용한다.
**설치 방법은 환경마다 다르므로 [bcc/INSTALL.md](https://github.com/iovisor/bcc/blob/master/INSTALL.md) 와 [bpftrace/INSTALL.md (https://github.com/iovisor/bpftrace/blob/master/INSTALL.md)를 참고한다.**

## 3. monitoring component 배포
SantaBPF는 시스템 장애/성능저하 발생 시 이를 어떻게 탐지할 수 있는가? 어떤 이슈는 현재 시스템의 스냅샷 정보만을 가지고도 식별할 수 있을테지만, 어떤 이슈는 지난 ?분동안의 avg cpu util에 anomaly가
발생했다는 것처럼 metric의 지난 이력들을 참고하는 식으로 탐지할 수 있을 것이다. 또한 이렇게 metric의 history를 로깅하는 것은 임의의 임계치에 대한 기준치를 제공해 줄 수 있다.

모니터링은 여기서 끝나지 않는다. 관리자의 의사결정을 도와줄 정보들을 효과적으로 시각화 하기 위해 dashboard 또한 제공되어야 한다. 

SantaBPF는 metric 수집과 시각화에 [netdata](https://github.com/netdata/netdata)를 사용하고
metric query를 위해 [prometheus](https://github.com/prometheus/prometheus)를 사용한다.

각 component들은 현재 docker container로 배포 스크립트가 작성되어 있으므로 [/deployments](https://github.com/SantaBPF/santabpf/tree/main/deployments)를 참고

# 2. SantaBPF 아키텍처
SantaBPF는 모니터링과 트러블슈팅을 수행하는 `Elf`, Elf와 상호작용하고 관리자의 의사결정을 돕기위한 대시보드를 제공하는 `Santa` 두 파트로 나뉘어져 있다.
Elf들은 각 노드마다 등록된 `Scenario`들을 지속적으로 체크하고 양성으로 식별되면 Santa에게 이를 알려준다.

## 1. Elf
![working_elf](http://clipart-library.com/img/721279.gif)
북극 어딘가 기지같은 곳에서 착한 아이와 나쁜 아이를 모니터링 하는것에서 유래했다. Elf의 역할은 각 노드의 시스템 상태를 주기적으로 수집하고 등록된 Scenario에 의해
TODO


---

<a name="footnote-bpf">1</a>: BPF는 원래 Berkeley Packet Filter의 두문자어였지만 BPF를 In-kernel VM으로 개선한 뒤에는 더이상 Berkeley, Packet, Filter 이 셋과 더 이상 연관이 없게되어
BPF를 두문자어로 보기보다 하나의 기술스택 이름으로 보는게 타당하다. 그래서 현재는 기존의 BPF는 cBPF(classic), eBPF(enhanced)라 불리던 이름은 BPF로 사용하는 추세다. 게다가 기존의 cBPF를 사용하던
tcpdump도 eBPF를 사용하므로 BPF라고 하면 eBPF를 의미한다고 보면 된다.

<a name="footnote-vm">2</a>: VM이라고 하니 무언가 중간에 레이어가 하나 낀 느낌이지만 그렇지 않다. BPF는 어떻게 kernel space에서 fail-safe를 보장하는가? BPF는
kernel에 로드되기전에 BPF verifier라는 것에 의해 체크된다. 이 과정에서 unreachable instructions, unbounded loops, out-of-bounds access와 같은게 존재하면 로드에 실패한다.
