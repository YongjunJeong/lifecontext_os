# LifeContext OS

[![라이선스: MIT](https://img.shields.io/badge/%EB%9D%BC%EC%9D%B4%EC%84%A0%EC%8A%A4-MIT-yellow.svg)](LICENSE)
[![품질 검사](https://github.com/YongjunJeong/lifecontext_os/actions/workflows/quality.yml/badge.svg)](https://github.com/YongjunJeong/lifecontext_os/actions/workflows/quality.yml)
[![파이썬](https://img.shields.io/badge/%ED%8C%8C%EC%9D%B4%EC%8D%AC-3.10+-blue)](https://www.python.org/)
[![로컬 우선](https://img.shields.io/badge/%EB%A1%9C%EC%BB%AC%20%EC%9A%B0%EC%84%A0-%EA%B0%9C%EC%9D%B8%20%EC%BB%A8%ED%85%8D%EC%8A%A4%ED%8A%B8-green)](AGENTS.md)

**LifeContext OS**는 LLM을 장기 조력자로 쓰기 위한 로컬 우선 개인 컨텍스트 운영 시스템입니다.

LLM은 똑똑하지만 매번 나를 잊고, 실제 이름·금액·관계·건강·계약 같은 민감한 정보를 통째로 외부에 맡기기는 어렵습니다. LifeContext OS는 오래 유지되어야 하는 자기 정보를 로컬 마크다운에 저장하고, Codex·Claude·ChatGPT·로컬 LLM은 그 문서를 읽는 교체 가능한 추론 엔진으로 사용합니다.

핵심은 단순합니다.

```text
개인 데이터는 로컬에 둔다.
LLM은 언제든 바꿀 수 있다.
판단은 내 방향성과 지금 시점성을 함께 본다.
```

---

## 왜 필요한가

일반적인 LLM 상담은 매번 컨텍스트를 다시 설명해야 합니다. 더 큰 문제는 장기 기억이 부정확하거나, 민감한 정보를 어디까지 넘겨도 되는지 애매하다는 점입니다.

LifeContext OS는 이 문제를 네 층으로 나눕니다.

| 층 | 역할 |
|---|---|
| 로컬 마크다운 원장 | 실제 기억, 가치관, 커리어, 관계, 돈, 건강, 계획 |
| 운영 규칙 | 사실 정정, 프라이버시, 최신성, 답변 톤, 금지 행동 |
| LLM 추론 엔진 | 질문에 맞춰 문서를 읽고 판단을 압축 |
| 최신 외부 정보 | 채용 시장, 연봉 밴드, 법·제도, 산업 흐름 |

그래서 이런 질문에 더 잘 답하게 만듭니다.

- "지금 이직할까, 3개월 뒤 2년 채우고 움직일까?"
- "이 사이드 프로젝트를 이번 분기에 시작해도 될까?"
- "이 결정이 내 정체성에서 나온 건가, 불안에서 나온 건가?"
- "지금 내 나이·현금흐름·건강·채용 시장을 고려하면 적절한 타이밍인가?"

---

## 핵심 설계

### 1. 로컬 우선 기억

개인정보의 원본은 LLM 서비스가 아니라 이 저장소의 마크다운 파일입니다. 실제로 채운 파일은 공개 저장소에 커밋하지 않고, 로컬·비공개 저장소·비공개 브랜치에 둡니다.

### 2. 사실 업데이트 규칙

같은 주제의 정보가 충돌하면 현재 판단에 사용할 값은 최신 확정값 하나로 단일화합니다. 의미 있는 정정은 삭제하지 않고 이력에 남깁니다.

예:

```text
초기 기억: 고객사 A 계약 10억
정정: 확인해보니 15억이 맞음
현재 확정값: 15억
정정 이력: 처음 10억으로 기억했으나 2026-05-14에 15억으로 정정
```

### 3. 시의성 의사결정

큰 결정은 인생 전체의 방향성만 보지 않습니다. 지금 나이, 재직 기간, 이번 분기 목표, 현금흐름, 건강, 관계 부하, 외부 시장 조건까지 함께 봅니다.

| 렌즈 | 질문 |
|---|---|
| 방향성 | 내 가치관, 정체성, 5년 북극성과 맞는가? |
| 시의성 | 지금 나이, 분기, 커리어 단계, 현금흐름, 건강 상태에서 적절한가? |
| 여력 | 시간·돈·체력·멘탈·관계 부채를 감당할 수 있는가? |
| 순서 | 지금 실행인가, 준비만인가, 3개월 뒤인가, 내년 재검토인가? |
| 리스크 | 지금 하면 잃는 것과 미루면 잃는 것은 각각 무엇인가? |

### 4. 최신 외부 정보 분리

볼트는 "나에 대한 기준"을 담고, 웹이나 최신 출처는 "지금 세상 조건"을 담습니다. 채용 시장, 연봉, 법·세금·비자, 금리, 회사 평판처럼 시간이 지나면 바뀌는 정보는 최신 확인 또는 `최신 확인 필요` 표시를 요구합니다.

### 5. LLM 독립성

이 프로젝트는 특정 모델에 종속되지 않습니다. 문서를 읽을 수 있는 LLM이면 사용할 수 있습니다.

| 사용 방식 | 예 |
|---|---|
| 로컬 전용 | 민감한 원문은 로컬 LLM에만 전달 |
| 외부 LLM + 선택 컨텍스트 | 질문에 필요한 일부 요약만 Codex, Claude, ChatGPT에 전달 |
| 혼합형 | Codex는 시스템 정리, 로컬 LLM은 민감한 자기상담 |

---

## 사용 흐름

1. `templates/`의 핵심 문서를 인터뷰로 채웁니다.
2. 중요한 결정이 생기면 관련 문서를 LLM 컨텍스트로 제공합니다.
3. LLM은 `AGENTS.md` 또는 `CLAUDE.md`의 운영 규칙에 따라 답합니다.
4. 새 사실이나 정정이 생기면 마크다운 원장을 업데이트합니다.
5. 시간이 지나 바뀌는 외부 정보는 웹검색 또는 최신 확인 필요로 분리합니다.

최소 세팅은 30분 안에 가능합니다.

| 우선순위 | 문서 | 역할 |
|---|---|---|
| 1 | `templates/self_profile.md` | 현재 나, 강점, 약점, 위험 신호 |
| 2 | `templates/philosophy.md` | 인생 우선순위, 가치, 정체성 |
| 3 | `templates/life_compass.md` | 매일/큰 결정의 판단 렌즈 |
| 4 | `templates/roadmap.md` | 현재 분기, 시간 배분, 시의성 |
| 5 | `templates/life_os.md` | 수면·충동·환경·관계·일 시스템 |

도메인 문서는 필요할 때 확장합니다.

| 문서 | 쓰는 때 |
|---|---|
| `templates/career_style.md` | 이직, 커리어 전환, 번아웃 |
| `templates/investment_style.md` | 투자 원칙, 매수·매도, 자산 배분 |
| `templates/love_style.md` | 연애 패턴, 결혼 필터 |
| `templates/relationship_protocol.md` | 특정 관계 사건, 메시지, 침묵 |
| `templates/side_project_strategy.md` | 사이드 프로젝트 운영 |

---

## 예시

익명 샘플은 [examples/decision_job_change.md](examples/decision_job_change.md)에 있습니다.

요약하면 이런 식입니다.

```text
질문: 지금 이직할까?

방향성: 맞음. 성장·자율·시장가치 상승과 연결됨.
시의성: 3개월 대기 권장. 곧 현 회사 2년이 되어 이력서 서사가 좋아짐.
여력: 준비는 가능하지만 즉시 이직은 체력·포트폴리오가 부족함.
순서: 지금은 준비, 2년 달성 직후 적극 지원.
리스크: 미루면 시장 기회를 일부 놓치지만, 지금 나가면 잦은 이직 인상이 커질 수 있음.
```

---

## 프로젝트 구조

```text
lifecontext-os/
├── AGENTS.md                       # Codex 등 AI 에이전트용 운영 규칙
├── CLAUDE.md                       # Claude Code용 운영 규칙
├── SETUP.md                        # 전체 인터뷰 가이드
├── QUICKSTART.md                   # 빠른 시작
├── examples/                       # 익명 사용 예시
├── templates/                      # 개인 컨텍스트 템플릿
├── scripts/
│   ├── calc_saju.py                # 선택 사주 모듈
│   ├── check_quality.py            # 문서·개인정보 품질 검사
│   └── requirements.txt
└── tests/
    └── test_saju_regression.py     # 선택 사주 모듈 회귀 테스트
```

---

## 선택 모듈: 사주

사주는 LifeContext OS의 중심이 아니라 **명시 요청 시만 사용하는 선택 확장 모듈**입니다.

운영 원칙:

- 일반 의사결정의 근거로 쓰지 않습니다.
- 사용자 자기인식과 실제 데이터보다 우선하지 않습니다.
- LLM이 사주 데이터를 추측해서 만들지 않습니다.
- `scripts/calc_saju.py`는 `sajupy`와 `lunar-python`의 8자 결과를 교차검증합니다.
- 격국·용신·일간 강약은 유파 차이가 있으므로 참고값으로 표시합니다.

실행:

```bash
pip install -r scripts/requirements.txt
python scripts/calc_saju.py --date YYYY-MM-DD --time HH:MM --gender male --place Seoul --true-solar
python tests/test_saju_regression.py
```

---

## 품질 검사

```bash
python scripts/check_quality.py
python tests/test_saju_regression.py
```

`check_quality.py`는 공개 저장소에 들어가면 안 되는 흔적과 문서 품질을 확인합니다.

- `.DS_Store`, `.venv`, 캐시 파일 추적 여부
- `templates/`에 들어간 실제 이메일·전화번호·주민등록번호 패턴
- README 링크 대상 존재 여부
- 예시 파일 존재 여부

GitHub Actions에서도 같은 검사를 실행합니다.

---

## 포트폴리오 관점

이 저장소는 `mylife-vault`를 기반으로 다음 방향으로 확장한 포크입니다.

- 개인 컨텍스트를 로컬 원장으로 다루는 운영 모델
- LLM 교체 가능성을 전제로 한 문서 구조
- 사실 정정과 최신 확정값 규칙
- 시의성 기반 의사결정 프레임
- 민감정보 보호를 위한 품질 검사
- 익명 예시와 자동 테스트
- 별자리 기능 제거
- 사주 기능은 선택 확장 모듈로 재배치

출처와 변경 내역은 [NOTICE.md](NOTICE.md)에 정리되어 있습니다.

---

## 크레딧

| 출처 | 용도 | 라이선스 |
|---|---|---|
| [yys5584/mylife-vault](https://github.com/yys5584/mylife-vault) | 원본 볼트 템플릿과 셋업 컨셉 | MIT |
| [sajupy](https://github.com/0ssw1/sajupy) | 선택 사주 모듈의 한국 만세력 교차검증 | MIT |
| [lunar-python](https://github.com/6tail/lunar-python) | 선택 사주 모듈의 계산 보조 | MIT |
| [ssaju](https://github.com/golbin/ssaju) | 선택 사주 모듈의 LLM 압축 요약 방식 참고 | MIT |

---

## 라이선스

MIT. 원본 저작권 고지는 적용 가능한 범위에서 보존합니다.

이 볼트에 나중에 입력되는 개인 데이터는 템플릿 라이선스의 일부가 아니며, 공개 저장소에 커밋하면 안 됩니다.
