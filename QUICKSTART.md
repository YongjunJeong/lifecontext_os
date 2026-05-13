# 빠른 시작 — LifeContext OS

LifeContext OS는 LLM 기반 개인 의사결정을 위한 로컬 우선 마크다운 볼트입니다.

Claude Code, Codex, ChatGPT, 로컬 LLM 어디서든 사용할 수 있습니다. 마크다운 파일이 원본 데이터이고, 모델은 교체 가능한 추론 인터페이스입니다.

---

## 설치

```bash
git clone <your-repo-url> lifecontext-os
cd lifecontext-os
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

그 다음 LLM 코딩 에이전트에서 이 폴더를 열고 이렇게 말합니다.

```text
LifeContext 인터뷰 시작해줘.
SETUP.md와 AGENTS.md 규칙을 따르고, 실제 개인정보는 내가 허락한 파일에만 저장해줘.
```

Claude Code를 쓰는 경우:

```text
/lifecontext-setup
```

---

## 먼저 채울 파일

추천 순서:

1. `templates/self_profile.md`
2. `templates/philosophy.md`
3. `templates/life_os.md`
4. `templates/life_compass.md`
5. `templates/roadmap.md`
6. 필요할 때만 도메인 파일: 커리어, 투자, 연애, 관계, 사이드 프로젝트
7. 선택: `templates/saju.md`

---

## 의사결정 질문 예시

핵심 파일을 채운 뒤 이렇게 물어봅니다.

```text
이 결정 어떻게 봐?
방향성 / 시의성 / 여력 / 순서 / 리스크 기준으로 판단해줘.
외부 최신 정보가 필요한 항목은 웹검색하거나 최신 확인 필요로 표시해줘.
```

---

## 선택 사주 계산

```bash
python scripts/calc_saju.py \
  --date YYYY-MM-DD \
  --time HH:MM \
  --gender male \
  --place Seoul \
  --true-solar
```

검증:

```bash
python tests/test_saju_regression.py
```

---

## 프라이버시

- 실제 개인정보를 공개 포트폴리오 저장소에 커밋하지 마세요.
- 공개 저장소에는 가짜 샘플 데이터만 사용하세요.
- 실제로 채운 템플릿은 비공개 브랜치, 비공개 저장소, 또는 로컬 전용 사본에 보관하세요.

---

## 출처

이 프로젝트는 MIT 라이선스의 `yys5584/mylife-vault`를 기반으로 개인화·확장한 포크입니다. 자세한 내용은 [NOTICE.md](NOTICE.md)를 참고하세요.
