# 개요
본 프로젝트에서 사용하는 netdata에 어떻게 새로 플러그인을 등록하고 배포하는지 알아본다.

# 프로젝트 구조
```bash
$ ls -d */
deployments/  docs/  front/  netdata/  PoC/
```
프로젝트 루트의 폴더 구조는 위와 같다.

deployments는 프로젝트와 관련없는 manifest들, docs는 이런 문서들, PoC는 테스트와 데모를 위한 폴더이다.
front 역시 조만간 netdata 안으로 옮길 예정이니 netdata만 자세히 보면 될것 같다.

```bash
netdata
├── chart
│   ├── sdconfig
│   └── templates
├── santabpf
│   ├── configs
│   │   └── conf.d
│   │       └── python.d
│   └── plugins
│       └── python.d
├── scripts
└── yamls
```

netdata 폴더는 chart, santabpf, scripts, yamls로 구성된다.

# plugin 추가
새로 plugin을 추가하기 위해 
[python plugin 문서](https://learn.netdata.cloud/docs/agent/collectors/python.d.plugin)를 참고하면
크게 메트릭을 수집할 plugin과 해당 plugin의 config이 추가되야 함을 알 수 있다.

각각 plugins/python.d/ 와 santabpf/configs/conf.d/python.d/ 아래 추가해주면 된다.

이미 기존에 있는 example.chart.py를 예시로 추가해봤으니 참고하면 좋겠다.

# 배포
추가하고 나서 이를 반영하기 위해 이미지 빌드와 재배포가 필요하다. 크게 도커 이미지 빌드와 k8s 배포 단계로 나뉘는데 이는 이미 셸스크립트로 작성되어 있기 때문에 신경쓰지 않아도 된다.
새로 플러그인을 작성하고 plugins과 configs에 적절하게 파일을 추가했으면 `./scripts/apply.sh`를 실행시키자. 

netdata-child가 Terminating되고 다시 Running으로 뜰때까지 기다렸다가 결과를 확인하면 된다. 다시 재배포가 완료되었다고 자동으로 스크립트가 종료되지 않으니 Ctrl+C를 눌러서 나오면 된다.
그리고 굳이 끝까지 안기다려도 `+ kubectl rollout restart daemonset netdata-child` 로그가 찍혔으면 Ctrl+C를 눌러도 된다.

# 테스트
실제로 netdata가 돌아가는 컨테이너 내부가 궁금할 수 있다. 아니면 아래와 같이 디버깅을 하고 싶을 수 있다.
```bash
# execute the plugin in debug mode, for a specific module
/opt/netdata/usr/libexec/netdata/plugins.d/python.d.plugin <module> debug trace
/usr/libexec/netdata/plugins.d/python.d.plugin <module> debug trace
```

그런 경우 `./scripts/exec.sh`로 netdata-child 컨테이너에 접속해서 보면된다.
