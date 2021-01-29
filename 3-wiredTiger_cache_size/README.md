# scenario 3: read performance with page cache 

원래 read performance with wiredTiger cache size여서 제목과 맞지않는 내용으로 시작된다. 처음에 MongoDB에서 데이터를 조회할때 디스크 아니면 MongoDB storage engine인 wiredTiger의 캐시만 활용하는줄 알았는데 실험이 진행될수록 캐시는 중간 중간 여러 단계에 있음을 알게되었다. 

![image](https://user-images.githubusercontent.com/19762154/106082793-b667ad00-615e-11eb-8b8c-53e98fbc7c27.png)

그래서 이번 시나리오에서는 그림의 Page cache와 읽기 성능에 대해 알아본다. 초반 내용은 page cache가 아닌 wiredTiger cache를 병목으로 가정하고 진행한 내용이지만 내용이 얼마 되지 않아 그냥 처음부터 읽어도 괜찮을것 같다. 아니면 8. Summary만 읽어도 좋을것 같다.

---

NoSQL DBMS로 유명한 MongoDB는 2014년 버전 3.2부터 WiredTiger라는 storage engine을 사용중이다. WiredTiger는 filesystem cache외에 내부적으로 cache를 하나 더 갖는데, 
50% of (RAM - 1 GB) 또는 256 MB에서 큰 값을 고르게 된다.

이번 시나리오에서는 _MongoDB를 운용하는 서버에서 다른 작업으로 인해 메모리가 부족해지고
덩달아 WiredTiger의 cache size도 줄어들면서 response time이 늘어난 문제를 다룬다_ 라고 하려 했으나
실험결과 WiredTiger의 cache size는 변함이 없어서 (4) performance degradation 확인 절부터는 주제를
Page cache로 변경하였다.

먼저 모의 테스트는 아래와 같이 진행했다:

### 1. Dockerfile 작성
```Dockerfile
FROM mongo:4.4.3

WORKDIR tmp

RUN apt update && apt install -y wget

RUN wget https://github.com/feliixx/mgodatagen/releases/download/v0.8.4/mgodatagen_linux_x86_64.tar.gz -O- | tar -xz

COPY ./dummy-data.json ./
COPY ./entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

CMD ["/tmp/entrypoint.sh"]
```
base image는 공식 이미지 mongo:4.4.3을 활용했고 더미데이터 생성은 [mgodatagen](https://github.com/feliixx/mgodatagen)을 활용했다.

### 2. entrypoint.sh
mongod daemon을 fork하고 더미데이터 생성을 하는 역할만 하기 때문에 스크립트 내용은 생략한다.

### 3. run.sh
```bash
#!/bin/bash

pushd test-app

docker build -t 3-wt_cache_size .

docker run -it --rm -p 5001:27017 --name 3-wt_cache_size 3-wt_cache_size
```
위와 같이 생긴 run.sh을 통해 3-wt_cache_size라는 이미지를 빌드하고 컨테이너로 띄운다.

### 4. performance degradation 확인
실제로 메모리가 부족해지면 wiredTiger의 읽기 성능이 어떻게 변하는지 확인해보자.
현재 t2.micro instance는 1G의 메모리만 할당되어 있어서 최대 cache size는 [256MB](https://docs.mongodb.com/manual/core/wiredtiger/#memory-use)가 된다.

![image](https://user-images.githubusercontent.com/19762154/105924505-b8a80980-6081-11eb-9d9b-441c3ef38c46.png)

이 상태에선 cache size가 이미 256 MB 보다 작아서 호스트의 가용 메모리가 0에 가까워져도 변화가 없을것이다.

![image](https://user-images.githubusercontent.com/19762154/105922882-d9229480-607e-11eb-98b8-49fdc9e3d716.png)

wiredTiger는 설정된 cache size의 80%를 유지한다고 한다. 
현재 cache size와 더미데이터가 메모리에 올라왔을때를 확인해보면 201MB(256 * 80%), 357MB임을 확인할 수 있었다.

하지만 정말 호스트의 가용 메모리 크기가 성능에 영향을 미치지 않는지 확인하고 싶었다.

그래서 다음 스크립트들을 작성했다.
1. /tmp 아래 tmpfs 파일시스템을 마운트하고 호스트의 available memory가 100Mi 아래로 내려갈때까지 `dd`로 메모리를 잡아먹는 스크립트
2. (1)에서 생성된 파일을 지워 호스트의 메모리 사용량을 정상으로 복구하는 스크립트
3. 더미데이터에 랜덤한 쿼리(캐시 도움이 없으면 I/O 비용이 많이 나갈만한)를 날리는 스크립트
4. (3)을 일정횟수만큼 반복하여 날리는동안 wiredTiger를 모니터링하는 스크립트

(1), (2)는 쉘 스크립트 / (3), (4)는 파이썬 스크립트로 작성되었으며 전체 내용은 3-wiredTiger_cache_size 경로 아래 코드들을 참고

![image](https://user-images.githubusercontent.com/19762154/105953514-a1cfda00-60b6-11eb-9b1e-53153fed05bb.png)

반복해서 실험한 결과 해당 쿼리를 수행하는 평균 시간도 메모리가 줄어든 크기(1/2)에 반비례해 2배로 늘어났고 cache hit count도 절반가까이 떨어진것을 볼 수 있었다. 하지만 통계에서 잡히는'bytes currently in the cache'는 항상 256MB의 80%인 200MB였다. cache size는 변하지 않는데 왜 cache hit count는 절반으로 떨어진걸까 궁금했다. 하지만 너무 특정 application의 작동 방식에 대해 의존하고 싶지 않아 이 부분은 다음 실험으로 미루기로 했다.

방향을 바꿔  CPU의 Utilization으로 비교해보았다.

![image](https://user-images.githubusercontent.com/19762154/105958549-1a866480-60be-11eb-833e-2d1b7b7ab436.png)

가용 메모리가 줄어들자 io에 병목이 생기는걸 볼 수 있었다. sar(1)에서 %iowait은 다음과 같은 의미를 갖고있다:
>               %iowait
>                     Percentage of time that the CPU or CPUs were idle during which the system had an outstanding disk I/O request.

확실하게 퍼포먼스에 문제가 생겼음을 확인했고 io가 병목이란것도 알았다.

### 5. USE Method

(4)의 과정은 우리가 이슈의 원인을 알고 있는 경우를 가정하고 진행되었다. 이를 SantaBPF에서 어떻게 적용해볼 수 있을까? 먼저 모니터링 작업이 가장 먼저 수반될것이다. 이 단계는 어떤 tool을 써도 상관 없지만 sar(1)가 가장 범용적일것 같아 sar(1)를 가정하고 진행하겠다.

가장먼저 USE Method를 사용해볼 수 있을것이다.

CPU, Memory capacity, Network interface, Storage Device I/O 등등의 resource들에 대해 utilization, saturation, errors에 대한 metric을 모니터링한다. 이번 시나리오의 경우에는 CPU utilization, Memory capacity saturation, Storage Device I/O Utilization에 대한 metric이 변하게될것이다. 어떤 값이 baseline이고 어디까지가 threshold가 될지는 시스템마다 다를텐데 이 부분도 다음 리서치로 일단 넘기기로 했다. 일단 여기서는 지난 이력을 baseline으로 삼았다고 해보자.

여기서 지난 이력은 단순히 최근 5분 1시간 하루가 아니라 주기성을 고려하도록 한다. 이러한 주기성으로는 하루, 일주일, 1달, 1년등이 있다. 주기를 하루로 보면 업무시간인 9~18시에 부하가 몰릴것이고 일주일로 보면 주중인 월~금에 부하가 몰릴것이다.

지난 이력과 비교해
CPU utilization은 내려가고 Memory capacity saturation은 올라가고 Storage Device I/O Utilization이 올라가는 상황에서,
무엇을 의심해볼 수 있을까?
이미 앞에서 답을 알고 있는 상황이기에 "가용메모리 크기가 줄어들어 cache size가 줄어들고 cache miss가 늘어나 데이터를 처리하는 시간보다 디스크에서 읽고쓰는 시간이 늘어나는 경우"를 생각해볼 수 있다. 하지만 이런 결론은 아직 아는게 여기까지라 이것밖에 생각나지 않아서 내린 결론일 가능성이 아주 크다 생각한다. 그래서 USE Method 다음으로 어떻게 접근할 수 있을지 고민했다.

### 6. tracing with cachestat(8)

bcc에서는 어떻게 cache에 대한 퍼포먼스를 측정하고 있는지 보니 cachestat(8)이라는 tool을 이미 만들어둔것을 확인했다.
모든 bcc tool들은 open source라 [내부구현](https://github.com/iovisor/bcc/blob/master/tools/cachestat.py)을 확인할 수 있었는데 `add_to_page_cache_lru` `mark_page_accessed` `account_page_dirtied` `mark_buffer_dirty` 4개 kernel function에 대해 의존하고 있었다. tracepoint가 아닌 kprobe인 만큼 커널과 distro 버전에 민감할 것이다.

테스트로 돌려본 결과는 아래와 같았다.

![image](https://user-images.githubusercontent.com/19762154/105962438-2aed0e00-60c3-11eb-82bc-ba90a0d7cd9d.png)

확실히 hit ratio가 바닥을 기는것을 볼 수 있었다. 하지만 이 통계가 어떻게 집계되는지 모르고 쓴다면 결과를 잘못 해석할수도 있다. 
먼저 hit ratio는 hit count / (hit count + miss count)로 계산된다. 이 count들은 어떻게 구해진걸까?
cachestat(8)의 내부구현을 보면 

- total = mark_page_accessed - mark_buffer_dirty
- misses = add_to_page_cache_lru - account_page_dirtied
- hits = total - misses

로 되어있다.

이 커널 함수들이 무슨 의미인지 더 알아보려 했지만 그러지 못했다. 좀 더 공부해서 지식이 쌓이면 이해할 수 있을지도 모르겠다. 대신 동일한 방법으로 구현된 다른 버전의 cachestat(8) 문서를 찾아봤다. 위 버전은 bcc를 활용했고 [ftrace를 활용한 cachestat](https://github.com/brendangregg/perf-tools/blob/master/fs/cachestat)도 있는데 ftrace 버전의 주석을 보면 

> \# This is a proof of concept using Linux ftrace capabilities on older kernels,
> \# and works by using function profiling for in-kernel counters. Specifically,
> \# four kernel functions are traced:
> \#
> \#	mark_page_accessed() for measuring cache accesses
> \#	mark_buffer_dirty() for measuring cache writes
> \#	add_to_page_cache_lru() for measuring page additions
> \#	account_page_dirtied() for measuring page dirties

라고 한다. 하지만 이건 linux 3.13에서 kprobe에 의존해 작성된 로직이니 다른 방법을 생각해보는것도 하나의 주제가 될 수 있겠다.

즉 cache access가 일어날때마다 mark_page_accessed() 함수 호출을 counting하고
그 중에 cache writes가 일어날때마다 counting된 mark_buffer_dirty() 함수 호출은 빼서
총 total(cache accesses)을 구한 뒤

add_to_page_cache_lru() 에서 account_page_dirtied()를 빼 misses를 구한다는데 이 부분을 잘 모르겠다. 코드에 주석도 없고 구글링 해도 잘 나오질 않아서 필요하다면 나중에 시간을 더 들여 봐야할것 같다.

hits를 구하는 건 위의 로직보다는 간단하다. 그냥 total에서 miss를 빼면되기 때문이다.

### 7. Pinpointing

_CPU utilization은 내려가고 Memory capacity saturation은 올라가고 Storage Device I/O Utilization이 올라가는 상황_ 

_mark_page_accessed, mark_buffer_dirty, add_to_page_cache_lru, account_page_dirtied kprobe로 보니 cache hit ratio가 바닥을 기는 상황_ 

아래 kprobe를 쓰는 방법이 오버헤드가 더 크니 처음 모니터링은 위의 resource별 USE에 대해서만 수행하고 의심되는 anomaly가 발생한 경우에만 아래와 같은 profiling & tracing 를 수행한다.

아래까지 왔으면 현재 시스템이 캐시 문제로 I/O에 병목이  생겼음을 알 수 있다.

원래는 왜 캐시에 문제가 생겼는지 더 알아보자. 라고 하고 프로세스별로 page cache 점유율을 보려고 했는데 방법을 찾지 못했다.
직접 실험이라도 해보려고 `sync; echo 3 | sudo tee > drop_caches`도 해봤지만 어째선지 cache가 0으로 가지 않았다. 무언가 하한이 있는건가 싶은데 이부분은 아무리 리서치를 하고 질문을 올려도 답을 받지 못했다. 

![image](https://user-images.githubusercontent.com/19762154/106223776-699ad980-6225-11eb-802a-a4e3c5fbac74.png)

대신 fincore(1)를 찾았다.
fincore(1)은 util-linux package에 포함되어 있는 명령어로, 어떤 파일이 메모리에 얼마나(몇 페이지에) 올라가 있는지 확인할 수 있다.

그리고 vfs의 __vfs_read()를 dynamic tracing 하여 어떤 파일이 현재 어떤 프로세스에게 얼마나 읽히고 있는지 확인해보는데
이 역시 bcc에서 filetop(8) 이라는 이름으로 구현되어 있다.

처음부터 page cache에 어떤 내용들이 올라가 있는지 알 수 있으면 이렇게 안하겠지만, 지금으로선 다음과 같이 접근해볼 수 있곘다.

![image](https://user-images.githubusercontent.com/19762154/106225410-6bb26780-6228-11eb-81b5-3f471b0df010.png)

1. 현재 어떤 파일의 I/O가 가장 심한지 확인한다. (현재 이슈가 I/O에 있음을 위에서 확인했으므로)

![image](https://user-images.githubusercontent.com/19762154/106225446-7a008380-6228-11eb-8ab9-e856f024d01c.png)

2. 그 파일이 메모리에 얼마나 올라가 있는지 확인한다.

![image](https://user-images.githubusercontent.com/19762154/106225631-e7141900-6228-11eb-8c95-6a6b6e2d96de.png)

3. (검증목적으로) 가용메모리가 줄어들었을때의 결과도 확인한다.

### 8. Summary

1. CPU Utilization 🡻 / Memory capacity saturation 🡹 / Storage Device I/O Utilization 🡹 인 상황이 인식됨
2. MongoDB의 response time도 2배 이상 느려진 상황
3. 캐시 문제인지 확인하기 위해 cachestat(8)로 hit ratio 확인
4. hit ratio가 현저히 낮다면 filetop(8)으로 현재 어떤 파일이 I/O 작업에 있는지 확인
5. fincore(1)로 해당 파일 크기 대비 얼마나 메모리에 적재되어 있는지 확인
6. 어떻게 하면 해당 파일을 디스크에서 읽지 않고 page cache에서 가지고 오게 할 수 있을지 솔루션 제시


---
#### NOTE 1
> Since tmpfs lives completely in the page cache and on swap, all tmpfs
pages will be shown as "Shmem" in /proc/meminfo and "Shared" in
free(1). Notice that these counters also include shared memory
(shmem, see ipcs(1)). The most reliable way to get the count is
using df(1) and du(1).

#### TODO 1
flamegraph missing symbol issue

![image](https://user-images.githubusercontent.com/19762154/105913756-a83b6300-6070-11eb-8cfc-ae73cecc52fa.png)

가용 메모리가 0에 가까워지는 경우 mongoDB의 성능이 급격히 나빠지는 구간의 code path 찾기. 이를 위해서 debugging symbol이 있는 버전으로 새로 빌드해야 하는데 현재 구축한 환경으로는 공간이 부족해서 (13GB<) 다음 실험으로 보류

#### TODO 2
`mount -t tmpfs none -o size=1G /tmp/foo`로 메모리에 임시 파일 시스템을 만들고
`dd if=/dev/urandom of=/tmp/foo/1 oflag=append conv=notrunc bs=50M count=1; free -h`로 남아있는 available memory size를 확인하면서 메모리를 잡아먹으면서 실험해보기.
너무 여유를 안주면 oom reaper가 mongod를 죽여버리는 문제가 있어 20Mi 정도는 남겨주어야 함.
cold cache문제도 고려해 실험 결과는 5번 중 3번 이후만 집계함.
하지만 현재 더미 데이터 크기가 이미 250MB 아래고 또 최대 캐시 사이즈도 이미 250MB 아래라 이런식으로는 실험이 진행되지 않음. 따라서 이것도 다음 실험으로 보류함

#### TODO 3
특정 프로세스의 page cache size 구하기

#### TODO 4
filetop에서 vfs_read 말고 다른 tracing할 I/O 함수가 있는지 확인

#### TODO 5
drop_caches 이슈
