# QUICKSTART — LifeContext OS

LifeContext OS is a local-first Markdown vault for LLM-assisted personal decisions.

Use it with Claude Code, Codex, ChatGPT, or a local LLM. The Markdown files are the source of truth; the model is replaceable.

---

## Fast Start

```bash
git clone <your-repo-url> lifecontext-os
cd lifecontext-os
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

Then open the folder with an LLM coding agent and say:

```text
LifeContext 인터뷰 시작해줘.
SETUP.md와 AGENTS.md 규칙을 따르고, 실제 개인정보는 내가 허락한 파일에만 저장해줘.
```

Claude Code users can run:

```text
/lifecontext-setup
```

---

## What To Fill First

Recommended order:

1. `templates/self_profile.md`
2. `templates/philosophy.md`
3. `templates/life_os.md`
4. `templates/life_compass.md`
5. `templates/roadmap.md`
6. Domain files only as needed: career, investment, love, relationship, side project
7. Optional: `templates/saju.md`

---

## Decision Prompt

After filling the core files, ask:

```text
이 결정 어떻게 봐?
방향성 / 시의성 / 여력 / 순서 / 리스크 기준으로 판단해줘.
외부 최신 정보가 필요한 항목은 웹검색하거나 최신 확인 필요로 표시해줘.
```

---

## Optional Saju Calculation

```bash
python scripts/calc_saju.py \
  --date YYYY-MM-DD \
  --time HH:MM \
  --gender male \
  --place Seoul \
  --true-solar
```

Verify:

```bash
python tests/test_saju_regression.py
```

---

## Privacy

- Do not commit real personal data to a public portfolio repository.
- Use fake sample data if this project is public.
- Keep personal filled templates in a private branch, private repo, or local-only copy.

---

## Attribution

This project is a personalized fork and extension of `yys5584/mylife-vault` under MIT. See [NOTICE.md](NOTICE.md).
