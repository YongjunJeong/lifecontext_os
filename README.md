# LifeContext OS

[![라이선스: MIT](https://img.shields.io/badge/%EB%9D%BC%EC%9D%B4%EC%84%A0%EC%8A%A4-MIT-yellow.svg)](LICENSE)
[![테스트: 통과](https://img.shields.io/badge/%ED%85%8C%EC%8A%A4%ED%8A%B8-10%2F10%20%ED%86%B5%EA%B3%BC-brightgreen)](tests/)
[![파이썬](https://img.shields.io/badge/%ED%8C%8C%EC%9D%B4%EC%8D%AC-3.10+-blue)](https://www.python.org/)
[![로컬 우선](https://img.shields.io/badge/%EB%A1%9C%EC%BB%AC%20%EC%9A%B0%EC%84%A0-%EA%B0%9C%EC%9D%B8%20%EC%BB%A8%ED%85%8D%EC%8A%A4%ED%8A%B8-green)](AGENTS.md)
[![검증 우선](https://img.shields.io/badge/%EA%B2%80%EC%A6%9D%20%EC%9A%B0%EC%84%A0-%EC%B6%94%EC%B8%A1%20%EA%B8%88%EC%A7%80-critical)](CLAUDE.md)

**LifeContext OS**는 LLM 기반 개인 의사결정을 위한 로컬 우선 개인 컨텍스트 볼트입니다.

오래 유지되는 자기 정보는 마크다운에 저장하고, LLM은 그 문서를 읽어 의사결정을 돕는 교체 가능한 추론 인터페이스로 사용합니다. 핵심은 “내 데이터는 내가 소유하고, LLM은 그때그때 바꿀 수 있으며, 판단은 인생 방향성과 현재 시점성을 함께 본다”입니다.

---

## 무엇을 해결하나

LifeContext OS는 이런 질문에 답하기 위한 구조입니다.

- "지금 이직할까, 3개월 뒤 2년 채우고 움직일까?"
- "이 사이드 프로젝트를 이번 분기에 시작해도 될까?"
- "이 결정이 내 정체성에서 나온 건가, 불안에서 나온 건가?"
- "지금 내 나이·현금흐름·건강·채용 시장을 고려하면 적절한 타이밍인가?"

시스템은 정보를 이렇게 분리합니다.

| 층 | 역할 |
|---|---|
| 로컬 마크다운 볼트 | 개인 기억, 가치관, 패턴, 커리어, 관계, 돈, 계획 |
| LLM | 교체 가능한 추론 인터페이스 |
| 웹/최신 출처 | 채용 시장, 연봉 밴드, 법·제도, 산업 흐름 같은 외부 현실 |
| 선택 사주 | 사용자가 명시 요청할 때만 참고하는 문화적·성찰용 보조 자료 |

---

## 핵심 기능

- **로컬 우선 개인 기억**: 자기 진단, 철학, 로드맵, 커리어, 관계, 투자, 사이드 프로젝트 정보를 마크다운으로 보관합니다.
- **사실 업데이트 규칙**: 이전 정보와 새 정보가 충돌하면 최신 확정값을 현재 기준으로 삼고, 의미 있는 변경은 정정 이력에 남깁니다.
- **시의성 의사결정 필터**: 큰 결정은 `방향성 / 시의성 / 여력 / 순서 / 리스크` 기준으로 판단합니다.
- **최신 외부 정보 확인 규칙**: 채용 시장, 연봉, 회사 평판, 법·세금·비자, 금리, 산업 트렌드는 최신 출처 확인 또는 `최신 확인 필요` 표시를 요구합니다.
- **LLM 독립 구조**: Codex, Claude, ChatGPT, 로컬 LLM 등 문서를 읽을 수 있는 모델이면 바꿔 쓸 수 있습니다.
- **프라이버시 중심 운영**: 민감한 원문은 로컬에 두고, 외부 LLM에는 필요한 요약만 넘길 수 있습니다.
- **검증형 사주 보조**: `sajupy ↔ lunar-python` 교차검증 기반 사주 계산, LLM용 압축 요약, 관계 강도, 세운·월운, 참고용 격국·용신 후보를 제공합니다.

---

## 프로젝트 구조

```text
lifecontext-os/
├── AGENTS.md                       # Codex 등 AI 에이전트용 운영 규칙
├── CLAUDE.md                       # Claude Code용 운영 규칙
├── SETUP.md                        # 인터뷰 가이드
├── QUICKSTART.md                   # 빠른 시작
├── LICENSE                         # MIT 라이선스
├── NOTICE.md                       # 출처와 변경 내역
├── templates/                      # 개인 컨텍스트 템플릿
│   ├── philosophy.md               # 인생 우선순위, 가치, 정체성
│   ├── self_profile.md             # 자기 진단, 강점, 약점, 배경
│   ├── life_os.md                  # 6 레이어 운영 시스템
│   ├── life_compass.md             # 매일/큰 결정용 컴파스
│   ├── roadmap.md                  # 데일리부터 연간까지의 계획
│   ├── relationship_protocol.md    # 관계 사건, 메시지, 침묵 룰
│   ├── side_project_strategy.md    # 사이드 프로젝트 운영 룰
│   ├── love_style.md               # 연애 스타일
│   ├── investment_style.md         # 투자 스타일
│   ├── career_style.md             # 커리어와 이직 시의성
│   └── saju.md                     # 선택 사주 컨텍스트
├── scripts/
│   ├── calc_saju.py                # 사주 계산과 LLM용 요약 생성
│   └── requirements.txt
└── tests/
    └── test_saju_regression.py     # 사주 교차검증 회귀 테스트
```

---

## 의사결정 모델

큰 결정을 물어보면 LifeContext OS는 다음 순서로 판단합니다.

| 렌즈 | 질문 |
|---|---|
| 방향성 | 내 가치관, 정체성, 5년 북극성과 맞는가? |
| 시의성 | 지금 나이, 분기, 커리어 단계, 현금흐름, 건강, 관계 부하에서 적절한가? |
| 여력 | 시간·돈·체력·멘탈을 감당할 수 있는가? |
| 순서 | 지금 실행인가, 지금은 준비만인가, 3개월 뒤인가, 내년 재검토인가? |
| 리스크 | 지금 하면 잃는 것과 미루면 잃는 것은 각각 무엇인가? |

예시:

```text
방향성: 맞음
시의성: 3개월 대기 권장
이유: 현 회사 2년 재직 시점이 이력서와 면접 서사에 더 유리할 수 있음
지금 할 일: 이력서, 포트폴리오, 레퍼런스, 목표 회사 리스트 준비
실행 시점: 건강·윤리 문제가 없다면 2년 달성 직후 적극 지원
```

---

## 사주 레이어

사주는 선택 기능이며 조언의 1순위 근거가 아닙니다.

운영 규칙:

- 사용자가 명시적으로 요청할 때만 사용합니다.
- 사용자 자기인식보다 사주를 우선하지 않습니다.
- LLM이 사주 데이터를 머리로 만들어내지 않습니다.
- `scripts/calc_saju.py`는 `sajupy`와 `lunar-python`으로 8자를 교차검증합니다.
- 격국·용신·일간 강약은 유파 차이가 있어 참고값으로 표시합니다.

실행:

```bash
pip install -r scripts/requirements.txt
python scripts/calc_saju.py --date YYYY-MM-DD --time HH:MM --gender male --place Seoul --true-solar
python tests/test_saju_regression.py
```

---

## 프라이버시 모델

| 모드 | 사용 방식 |
|---|---|
| 로컬 전용 | 실명, 금액, 관계, 건강, 가족사 원문을 로컬 마크다운에만 보관 |
| 외부 LLM + 선택 컨텍스트 | 질문에 필요한 일부 문서나 요약만 전달 |
| 혼합형 | Codex/Claude는 시스템 설계에, 로컬 LLM은 민감한 자기상담에 사용 |

볼트가 진짜 원장이고, LLM은 추론 인터페이스입니다.

---

## 포트폴리오 관점

이 저장소는 오픈소스 라이프 볼트 템플릿을 기반으로 개인 의사결정 시스템으로 확장한 포크입니다.

주요 변경점:

- **LifeContext OS**로 리브랜딩
- 로컬 우선 프라이버시 모델 정리
- 최신 확정값과 정정 이력 기반 사실 업데이트 규칙 추가
- 시의성 기반 의사결정 프레임 추가
- 커리어 타이밍과 채용 시장 최신성 확인 레이어 추가
- 별자리 기능 제거
- LLM용 사주 압축 요약과 관계 강도 출력 강화

출처와 변경 내역은 [NOTICE.md](NOTICE.md)에 정리되어 있습니다.

---

## 크레딧

| 출처 | 용도 | 라이선스 |
|---|---|---|
| [yys5584/mylife-vault](https://github.com/yys5584/mylife-vault) | 원본 볼트 템플릿과 셋업 컨셉 | MIT |
| [sajupy](https://github.com/0ssw1/sajupy) | 한국 만세력 교차검증 | MIT |
| [lunar-python](https://github.com/6tail/lunar-python) | 사주 계산 보조 | MIT |
| [ssaju](https://github.com/golbin/ssaju) | LLM용 압축 사주 요약과 관계 강도 표현 참고 | MIT |

---

## 라이선스

MIT. 원본 저작권 고지는 적용 가능한 범위에서 보존합니다.

이 볼트에 나중에 입력되는 개인 데이터는 템플릿 라이선스의 일부가 아니며, 공개 저장소에 커밋하면 안 됩니다.
