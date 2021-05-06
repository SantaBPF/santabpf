# 1. Python 개발 환경 구성
1. `git clone https://github.com/SantaBPF/santabpf`로 레포 복사
2. pyproject.toml을 참고하여 적절한 버전과 환경을 구축. 여기서는 [asdf](https://github.com/asdf-vm/asdf)와 [poetry](https://github.com/python-poetry/poetry)를 활용한다.
```
$ asdf install python 3.9.4
$ poetry env use 3.9.4
$ poetry install
```
3. poetry를 적절히 설치한 경우, 해당 프로젝트 경로에 들어가면 자동으로 전용 가상 환경을 activate할 것 이다. 확실하지 않다면 `poetry env info`로 확인
4. 프로젝트 루트 경로에서 `jupyter notebook`을 해서 브라우저에 Jupyter Notebook 환경이 열리면 성공. 단 (3)이 제대로 되지 않은 경우 이후 문제가 발생할 수 있다.

# 2. BPF 개발 환경 구성<sup>[1](#footnote-bpf)</sup>
1. BPF는 Linux 4.x 이후 커널에 내장된 기능으로 VM<sup>[2](#footnote-vm)</sup>내에서 임의의 코드를 돌려볼 수 있게 해준다.
임의의 코드를 작성해 커널의 자료구조에 접근할 수 있고 이를 실행하는데 별도의 커널 재컴파일이나 모듈 작성이 필요없고 system
덕분에 Security, Tracing & Profiling, Networking, Observability & Monitoring와 같은 분야에서 다양하게 활용되고 있다.


<a name="footnote-bpf">1</a>: BPF는 원래 Berkeley Packet Filter의 두문자어였지만 BPF를 In-kernel VM으로 개선한 뒤에는 더이상 Berkeley, Packet, Filter 이 셋과 더 이상 연관이 없게되어
BPF를 두문자어로 보기보다 하나의 기술스택 이름으로 보는게 타당하다. 그래서 현재는 기존의 BPF는 cBPF(classic), eBPF(enhanced)라 불리던 이름은 BPF로 사용하는 추세다. 게다가 기존의 cBPF를 사용하던
tcpdump도 eBPF를 사용하므로 BPF라고 하면 eBPF를 의미한다고 보면 된다.

<a name="footnote-vm">2</a>: VM이라고 하니 무언가 중간에 레이어가 하나 낀 느낌이지만 그렇지 않다. 여기서 VM이란건 Sandbox에 가깝다. BPF는 어떻게 kernel space에서 fail-safe를 보장하는가? BPF는
kernel에 로드되기전에 BPF verifier라는 것에 의해 체크된다. 이 과정에서 unreachable instructions, unbounded loops, out-of-bounds access와 같은게 존재하면 로드에 실패한다.
