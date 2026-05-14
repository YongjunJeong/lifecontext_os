"""선택 사주 모듈 회귀 테스트 — 기준값 + sajupy ↔ lunar-python 교차검증.

CLAUDE.md 절대 룰: "추측 금지, 실측 데이터만".
각 케이스는 고정 기준값과 두 라이브러리 결과 일치를 함께 확인한다.

실행:
    pytest tests/test_saju_regression.py -v
또는
    python tests/test_saju_regression.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Windows 콘솔 UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from sajupy import calculate_saju as sajupy_calc
from lunar_python import Solar


# 알려진 기준 케이스 — 고정 기준값과 두 라이브러리 결과 모두 일치해야 함
# 진태양시 보정 OFF (KST 표준자오선 기준 비교)
REFERENCE_CASES = [
    # (label, year, month, day, hour, minute, expected_8자)
    ("일반 오후 출생", 1990, 3, 15, 14, 30, "庚午/己卯/己卯/辛未"),
    ("야자시 23:30", 1990, 3, 15, 23, 30, "庚午/己卯/己卯/丙子"),
    ("조자시 00:30 (다음날)", 1990, 3, 16, 0, 30, "庚午/己卯/庚辰/丙子"),
    ("새벽 일반", 1990, 3, 16, 1, 30, "庚午/己卯/庚辰/丁丑"),
    # 절기 경계 — 입동 전후
    ("입동 직전 1990-11-06", 1990, 11, 6, 12, 0, "庚午/丙戌/乙亥/壬午"),
    # 입춘 경계 — 매년 2/4 전후로 년주 변동
    ("입춘 직전 2000-02-03", 2000, 2, 3, 12, 0, "己卯/丁丑/辛卯/甲午"),
    ("입춘 직후 2000-02-05", 2000, 2, 5, 12, 0, "庚辰/戊寅/癸巳/戊午"),
    # 윤달·절기 경계 케이스
    ("2024-01-01 자정 직후", 2024, 1, 1, 0, 30, "癸卯/甲子/甲子/甲子"),
    # 멀리 떨어진 케이스
    ("1900년 초", 1900, 1, 15, 12, 0, "己亥/丁丑/戊子/戊午"),
    ("2099년 말", 2099, 12, 25, 18, 0, "己未/丙子/丙申/丁酉"),
]


def calc_lunar_python(y, m, d, h, mi):
    """lunar-python 8자 계산."""
    s = Solar.fromYmdHms(y, m, d, h, mi, 0)
    ec = s.getLunar().getEightChar()
    return f"{ec.getYear()}/{ec.getMonth()}/{ec.getDay()}/{ec.getTime()}"


def calc_sajupy(y, m, d, h, mi):
    """sajupy 8자 계산 (한국 만세력)."""
    r = sajupy_calc(year=y, month=m, day=d, hour=h, minute=mi, use_solar_time=False)
    return f"{r['year_pillar']}/{r['month_pillar']}/{r['day_pillar']}/{r['hour_pillar']}"


def test_all_cases():
    """모든 케이스에서 sajupy ↔ lunar-python 일치 확인."""
    failures = []
    for label, y, m, d, h, mi, expected in REFERENCE_CASES:
        lp = calc_lunar_python(y, m, d, h, mi)
        sj = calc_sajupy(y, m, d, h, mi)
        match = lp == sj
        exp_match = (expected is None) or (lp == expected)
        if not match or not exp_match:
            failures.append({
                "case": label, "date": f"{y}-{m:02d}-{d:02d} {h:02d}:{mi:02d}",
                "lunar_python": lp, "sajupy": sj, "expected": expected,
                "lib_match": match, "expected_match": exp_match,
            })
    return failures


def main():
    print("=" * 90)
    print(f"사주 회귀 테스트 — {len(REFERENCE_CASES)}개 케이스")
    print("출처: sajupy (한국 만세력 1900-2100) ↔ lunar-python")
    print("=" * 90)
    print(f"{'#':<3} {'케이스':<28} {'lunar-python':<22} {'sajupy':<22} {'일치':<6}")
    print("-" * 90)

    failures = []
    for i, (label, y, m, d, h, mi, expected) in enumerate(REFERENCE_CASES, 1):
        lp = calc_lunar_python(y, m, d, h, mi)
        sj = calc_sajupy(y, m, d, h, mi)
        match = lp == sj
        marker = "✅" if match else "❌"
        exp_note = ""
        if expected and lp != expected:
            exp_note = f"  ⚠️ expected: {expected}"
            marker = "❌"
        print(f"{i:<3} {label:<28} {lp:<22} {sj:<22} {marker}{exp_note}")
        if not match or (expected and lp != expected):
            failures.append((label, lp, sj, expected))

    print("-" * 90)
    if failures:
        print(f"❌ FAIL: {len(failures)}/{len(REFERENCE_CASES)} 케이스 불일치")
        for label, lp, sj, expected in failures:
            print(f"  - {label}: lunar={lp}, sajupy={sj}, expected={expected}")
        sys.exit(1)
    else:
        print(f"✅ PASS: 전체 {len(REFERENCE_CASES)}/{len(REFERENCE_CASES)} 케이스 일치")
        print("→ lunar-python = sajupy = 한국 만세력 표준 확인")
    return 0


# pytest entry
def test_saju_libraries_agree():
    """pytest용 — 라이브러리 간 일치와 기준값 일치를 함께 검증."""
    failures = test_all_cases()
    if failures:
        msg = "\n".join(
            f"  {f['case']} ({f['date']}): lunar={f['lunar_python']}, "
            f"sajupy={f['sajupy']}, expected={f['expected']}"
            for f in failures
        )
        raise AssertionError(f"선택 사주 모듈 회귀 실패 {len(failures)}건:\n{msg}")


if __name__ == "__main__":
    main()
