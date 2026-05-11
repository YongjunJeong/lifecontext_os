# LifeContext OS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![Local First](https://img.shields.io/badge/local--first-personal%20context-green)](AGENTS.md)
[![No Speculation](https://img.shields.io/badge/no%20speculation-verified%20data%20only-critical)](CLAUDE.md)

**LifeContext OS** is a local-first personal context vault for LLM-assisted life decisions.

It stores long-lived personal context in Markdown, keeps facts updated with correction history, and helps an LLM answer decision questions through identity, current timing, capacity, market freshness, and optional saju context.

> Core idea: **my data stays in Markdown, the LLM is replaceable, and decisions are judged by both life direction and present timing.**

---

## What It Does

LifeContext OS is designed for questions like:

- "Should I change jobs now, or wait three months?"
- "Is this side project aligned with my current quarter?"
- "Am I making this decision from identity or from anxiety?"
- "Is this the right timing given my age, cash flow, health, and market conditions?"

The system separates:

| Layer | Role |
|---|---|
| Local Markdown vault | Personal memory, values, patterns, career, relationships, money, plans |
| LLM | Replaceable reasoning interface |
| Web/latest sources | Time-sensitive external reality such as hiring markets, salary bands, laws, trends |
| Optional saju | Explicitly requested cultural/reflective context only |

---

## Key Features

- **Local-first personal memory**: Markdown files hold the user's self-profile, philosophy, roadmap, career style, relationship patterns, and operating rules.
- **Fact update protocol**: when old and new facts conflict, the latest confirmed value becomes the current truth while meaningful corrections remain in history.
- **Time-sensitive decision filter**: major decisions are judged through `direction / timing / capacity / sequence / risk`.
- **External freshness rule**: hiring markets, salary bands, company reputation, laws, visa/tax rules, rates, and industry trends require fresh sources or an explicit "needs latest check" marker.
- **LLM-agnostic design**: works with Codex, Claude, ChatGPT, or a local LLM as long as the model can read the vault.
- **Privacy-aware workflow**: sensitive real data can remain local; external LLMs can receive only selected summaries.
- **Enhanced saju support**: Python-based saju calculation with `sajupy ↔ lunar-python` cross-check, plus LLM-ready compact summaries, relation priority, yearly/monthly flow, and clearly marked reference-only interpretation.

---

## Project Structure

```text
lifecontext-os/
├── AGENTS.md                       # Rules for Codex and other AI agents
├── CLAUDE.md                       # Rules for Claude Code
├── SETUP.md                        # Interview guide
├── QUICKSTART.md                   # Quick start guide
├── LICENSE                         # MIT
├── NOTICE.md                       # Attribution and modification notes
├── templates/                      # Personal context templates
│   ├── philosophy.md               # Life priority, values, identity
│   ├── self_profile.md             # Self diagnosis, strengths, weaknesses, background
│   ├── life_os.md                  # Operating system layers
│   ├── life_compass.md             # Daily and major decision compass
│   ├── roadmap.md                  # Daily to yearly planning
│   ├── relationship_protocol.md    # Relationship incidents and message rules
│   ├── side_project_strategy.md    # Side project operating rules
│   ├── love_style.md               # Relationship style
│   ├── investment_style.md         # Investment style
│   ├── career_style.md             # Career and job-change timing
│   └── saju.md                     # Optional verified saju context
├── scripts/
│   ├── calc_saju.py                # Saju calculation and LLM-ready summary
│   └── requirements.txt
└── tests/
    └── test_saju_regression.py     # Cross-check regression tests
```

---

## Decision Model

For major decisions, LifeContext OS asks:

| Lens | Question |
|---|---|
| Direction | Does this match my values, identity, and 5-year north star? |
| Timing | Is this right for my current age, quarter, career stage, cash flow, health, and relationship load? |
| Capacity | Do I have enough time, money, energy, and emotional bandwidth? |
| Sequence | Should I act now, prepare now, wait three months, or review next year? |
| Risk | What do I lose if I act now, and what do I lose if I delay? |

Example:

```text
Direction: yes
Timing: wait three months
Reason: 2-year tenure mark improves career signaling and interview narrative
Now: prepare resume, portfolio, references, and market map
Act: start active applications after the 2-year mark unless health or ethics require earlier exit
```

---

## Saju Layer

Saju is optional and never the primary basis for advice.

Rules:

- Use only when the user explicitly asks.
- Never let saju override the user's self-knowledge.
- Never generate saju data from memory.
- `scripts/calc_saju.py` cross-checks 8 characters through `sajupy` and `lunar-python`.
- Gyeokguk/yongsin/day-strength outputs are marked as reference because schools differ.

Run:

```bash
pip install -r scripts/requirements.txt
python scripts/calc_saju.py --date YYYY-MM-DD --time HH:MM --gender male --place Seoul --true-solar
python tests/test_saju_regression.py
```

---

## Privacy Model

Recommended operating modes:

| Mode | Use |
|---|---|
| Local-only | Real names, money, relationships, health, and family history stay in local Markdown |
| External LLM with selected context | Share only the subset or summary needed for a question |
| Hybrid | Use Codex/Claude for system design and local LLM for sensitive life advice |

The vault is the source of truth. LLMs are reasoning interfaces.

---

## Portfolio Notes

This repository is a personalized fork and extension of an open-source life vault template.

Major extensions include:

- Rebranded system architecture as **LifeContext OS**
- Local-first privacy model
- Fact correction and latest-confirmed-value protocol
- Time-sensitive decision framework
- Career timing layer with market freshness checks
- Removal of zodiac functionality
- Enhanced saju output inspired by LLM-ready analysis patterns

See [NOTICE.md](NOTICE.md) for attribution.

---

## Credits

| Source | Use | License |
|---|---|---|
| [yys5584/mylife-vault](https://github.com/yys5584/mylife-vault) | Original vault template and setup concept | MIT |
| [sajupy](https://github.com/0ssw1/sajupy) | Korean manselyeok cross-check | MIT |
| [lunar-python](https://github.com/6tail/lunar-python) | Saju calculation support | MIT |
| [ssaju](https://github.com/golbin/ssaju) | Inspiration for LLM-ready compact saju summaries and relation-priority output | MIT |

---

## License

MIT. Original copyright notices are preserved where applicable.

Personal data entered into this vault is not part of the template license and should not be committed to a public repository.
