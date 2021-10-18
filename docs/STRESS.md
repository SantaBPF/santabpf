대부분의 스트레스 테스트는 `stress-ng`를 활용할 계획입니다.

## 1. cpu usage 높이기
`stress-ng -c 0 -l 95` 95를 조절하여 전체 cpu 자원의 얼마만큼을 사용할건지 테스트   

## 2. cpu steal 높이기
(1)을 하다보면 ec2 cpu credit이 다 고갈되어 자연스레 이 시나리오로 떨어짐

## 3. memory usage 높이기
`stress-ng --vm 0 --vm-bytes 50m` 50m을 조절하여 메모리를 얼마나 사용할건지 테스트
