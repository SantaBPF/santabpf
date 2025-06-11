# SantaBPF - Linux Troubleshooting Assistant with BPF
![Santa](https://imgs.xkcd.com/comics/incident.png)
![BPF](http://www.brendangregg.com/eBPF/linux_ebpf_internals.png)

### Santa's Omniscience + BPF's Omnipotence -> Ultimate Linux Troubleshooting Assistant

### Docs

1. [how to add alarms](https://github.com/SantaBPF/santabpf/blob/main/docs/ADD-NEW-ALARM.md)
2. [hot to add plugins](https://github.com/SantaBPF/santabpf/blob/main/docs/ADD-NEW-PLUGIN.md)
3. [CONTRIBUTING](https://github.com/SantaBPF/santabpf/blob/main/docs/CONTRIBUTING.ko.md)

# SRE & DevOps 트러블 슈팅 지원 시스템

## 📌 프로젝트 소개
SRE팀, 서버 인프라 Admin, DevOps 엔지니어들이 **문제를 조기에 식별하고 신속하게 대응**할 수 있도록 지원하는 **트러블 슈팅 지원 시스템**입니다.  
실시간 모니터링, 빠른 알람, 사후 분석 기능을 통해 시스템의 안정성을 높이는 것을 목표로 합니다.

---

## 🎯 목적
- DevOps 또는 SRE 전담 인력이 없거나 **더 빠른 이슈 대응과 사후 분석**이 필요한 기업을 대상으로  
  **Linux Server 트러블 슈팅 및 Postmortem(사후 분석) Report 작성**을 지원하는 시스템 구축
- 보안 모니터링 및 오류 시각화 지원
- 각 노드의 **성능 저하, 보안 이슈, 시스템 오류를 실시간 모니터링**하고 빠르게 대응

---

## ⚙️ 기술 및 개발환경
- **Backend:** Python
- **Frontend:** HTML, CSS, JavaScript
- **Infra:** AWS EC2, Linux, Ubuntu
- **Monitoring:** Netdata

---

## 🚀 주요 기능
- Netdata를 활용한 **보안 모니터링 및 오류 시각화**
- 프로그램, 보안, 성능 이슈에 대한 **시나리오 설계**
- 시나리오 발생 시 **간편한 트러블 슈팅 제공 및 실시간 알람 지원**

---

## 🛠️ 트러블 슈팅

### 문제 상황
- **데이터 수집 실패**  
  각 노드에서 metric 수집 실패 시 전체 모니터링 시스템의 신뢰성 저하

- **리소스 과부하**  
  모니터링 에이전트로 인해 노드의 성능 저하 발생 가능성

- **실시간 대응 체계 부재**  
  알람 부족 및 미흡한 시각화 대시보드로 인한 대응 지연

- **시나리오 설계 부족**  
  실제 환경의 다양한 이슈를 충분히 고려하지 못해 트러블 슈팅 어려움

---

### 해결 방안
- **고가용성 구성**  
  `Santa(노드들로부터 수집된 정보를 적재하고 관리하는 역할)`를 Deployment로 구성하여 일부 노드 장애 시에도 안정적인 데이터 수집 및 시각화 유지

- **경량화된 데이터 수집**  
  `Elf`를 각 노드에 Daemon으로 배포, metric 수집 후 저장하지 않고 `Santa`로만 전송하여 서버 부하 최소화

- **자동 알람 시스템 구축**  
  수집된 metric을 실시간 시나리오와 매칭하여 문제 발생 시 어드민에게 즉시 알림 제공

- **커스텀 대시보드 제공**  
  발생한 이슈에 적합한 시각화 차트를 자동으로 생성하여 직관적인 문제 파악 지원

- **손쉬운 배포**  
  Container 기반 시스템 구축 및 k8s manifest, Shell 스크립트로 자동화하여 손쉬운 배포 및 확장성 확보

- **PoC 환경 구축**  
  다양한 이슈를 재현할 수 있는 모의 테스트 환경을 구축하여 시나리오 검증 및 트러블 슈팅 신뢰성 확보

---

## ✅ 결과
- **실시간 보안·성능 모니터링 및 빠른 대응 체계 확보**
- **서버 부하 최소화** 및 안정적인 metric 수집·관리 가능
- **손쉬운 배포 및 확장성**을 통한 다양한 환경 지원
- **시나리오 기반 알람의 정확도 및 실효성 향상**  
  (PoC 환경을 통한 이슈 재현 및 검증 완료)
