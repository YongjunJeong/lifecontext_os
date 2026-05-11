#!/usr/bin/env python3
"""사주 8자 + 대운 + 세운 + 신살 + 12운성 + 공망 + 납음 + 지장간 자동 계산.

**검증 정책 (CLAUDE.md 절대 룰):**
- 8자 = sajupy (한국 만세력 데이터 1900-2100, primary)
- 추가 기능(대운/세운/12운성/공망/신살/지장간) = lunar-python
- **매 실행마다 sajupy ↔ lunar-python 8자 자동 cross-check**, 불일치 시 ⚠️ 경고 + 진행 중단

사용:
    python calc_saju.py --date 1990-03-15 --time 14:30 --gender male --place "Seoul" --true-solar
    python calc_saju.py --date 1990-03-15 --time unknown --gender female --place "Seoul"

의존성:
    pip install sajupy lunar-python
"""

from __future__ import annotations

import argparse
import io
import sys
from datetime import datetime, timedelta
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from lunar_python import Solar
except ImportError:
    sys.stderr.write("lunar-python 미설치. pip install -r scripts/requirements.txt\n")
    sys.exit(1)

try:
    from sajupy import calculate_saju as sajupy_calculate
except ImportError:
    sys.stderr.write("sajupy 미설치 (한국 만세력 검증용). pip install -r scripts/requirements.txt\n")
    sys.exit(1)


# ── 한자 → 한글 매핑 ──

GAN_KO = {"甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무",
          "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계"}

ZHI_KO = {"子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사",
          "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해"}

WUXING_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}

GAN_WUXING = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
              "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

ZHI_WUXING = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
              "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

DISHI_KO = {
    "长生": "장생", "沐浴": "목욕", "冠带": "관대", "临官": "임관", "帝旺": "제왕",
    "衰": "쇠", "病": "병", "死": "사", "墓": "묘", "绝": "절", "胎": "태", "养": "양",
}

SHISHEN_KO = {
    "比肩": "비견", "劫财": "겁재", "食神": "식신", "伤官": "상관",
    "偏财": "편재", "正财": "정재", "七杀": "편관", "正官": "정관",
    "偏印": "편인", "正印": "정인",
}

SHISHEN_GROUPS = {
    "比肩": "비겁", "劫财": "비겁",
    "食神": "식상", "伤官": "식상",
    "偏财": "재성", "正财": "재성",
    "七杀": "관성", "正官": "관성",
    "偏印": "인성", "正印": "인성",
}

TEN_GOD_BY_DAY_STEM = {
    "甲": {"甲": "比肩", "乙": "劫财", "丙": "食神", "丁": "伤官", "戊": "偏财", "己": "正财", "庚": "七杀", "辛": "正官", "壬": "偏印", "癸": "正印"},
    "乙": {"乙": "比肩", "甲": "劫财", "丁": "食神", "丙": "伤官", "己": "偏财", "戊": "正财", "辛": "七杀", "庚": "正官", "癸": "偏印", "壬": "正印"},
    "丙": {"丙": "比肩", "丁": "劫财", "戊": "食神", "己": "伤官", "庚": "偏财", "辛": "正财", "壬": "七杀", "癸": "正官", "甲": "偏印", "乙": "正印"},
    "丁": {"丁": "比肩", "丙": "劫财", "己": "食神", "戊": "伤官", "辛": "偏财", "庚": "正财", "癸": "七杀", "壬": "正官", "乙": "偏印", "甲": "正印"},
    "戊": {"戊": "比肩", "己": "劫财", "庚": "食神", "辛": "伤官", "壬": "偏财", "癸": "正财", "甲": "七杀", "乙": "正官", "丙": "偏印", "丁": "正印"},
    "己": {"己": "比肩", "戊": "劫财", "辛": "食神", "庚": "伤官", "癸": "偏财", "壬": "正财", "乙": "七杀", "甲": "正官", "丁": "偏印", "丙": "正印"},
    "庚": {"庚": "比肩", "辛": "劫财", "壬": "食神", "癸": "伤官", "甲": "偏财", "乙": "正财", "丙": "七杀", "丁": "正官", "戊": "偏印", "己": "正印"},
    "辛": {"辛": "比肩", "庚": "劫财", "癸": "食神", "壬": "伤官", "乙": "偏财", "甲": "正财", "丁": "七杀", "丙": "正官", "己": "偏印", "戊": "正印"},
    "壬": {"壬": "比肩", "癸": "劫财", "甲": "食神", "乙": "伤官", "丙": "偏财", "丁": "正财", "戊": "七杀", "己": "正官", "庚": "偏印", "辛": "正印"},
    "癸": {"癸": "比肩", "壬": "劫财", "乙": "食神", "甲": "伤官", "丁": "偏财", "丙": "正财", "己": "七杀", "戊": "正官", "辛": "偏印", "庚": "正印"},
}

ELEMENT_GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
ELEMENT_CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
ELEMENT_GENERATED_BY = {v: k for k, v in ELEMENT_GENERATES.items()}
ELEMENT_CONTROLLED_BY = {v: k for k, v in ELEMENT_CONTROLS.items()}

GAN_HAP = {frozenset(("甲", "己")): "土", frozenset(("乙", "庚")): "金", frozenset(("丙", "辛")): "水",
           frozenset(("丁", "壬")): "木", frozenset(("戊", "癸")): "火"}
GAN_CHONG = {frozenset(("甲", "庚")), frozenset(("乙", "辛")), frozenset(("丙", "壬")), frozenset(("丁", "癸"))}

ZHI_CHONG = {frozenset(("子", "午")), frozenset(("丑", "未")), frozenset(("寅", "申")),
             frozenset(("卯", "酉")), frozenset(("辰", "戌")), frozenset(("巳", "亥"))}
ZHI_LIUHE = {frozenset(("子", "丑")): "土", frozenset(("寅", "亥")): "木", frozenset(("卯", "戌")): "火",
             frozenset(("辰", "酉")): "金", frozenset(("巳", "申")): "水", frozenset(("午", "未")): "土"}
ZHI_SANHE = {frozenset(("申", "子", "辰")): "水", frozenset(("亥", "卯", "未")): "木",
             frozenset(("寅", "午", "戌")): "火", frozenset(("巳", "酉", "丑")): "金"}
ZHI_FANGHE = {frozenset(("亥", "子", "丑")): "水", frozenset(("寅", "卯", "辰")): "木",
              frozenset(("巳", "午", "未")): "火", frozenset(("申", "酉", "戌")): "金"}
ZHI_BANHE = {
    frozenset(("申", "子")): "水", frozenset(("子", "辰")): "水", frozenset(("申", "辰")): "水",
    frozenset(("亥", "卯")): "木", frozenset(("卯", "未")): "木", frozenset(("亥", "未")): "木",
    frozenset(("寅", "午")): "火", frozenset(("午", "戌")): "火", frozenset(("寅", "戌")): "火",
    frozenset(("巳", "酉")): "金", frozenset(("酉", "丑")): "金", frozenset(("巳", "丑")): "金",
}
ZHI_XING = {frozenset(("寅", "巳")), frozenset(("巳", "申")), frozenset(("寅", "申")),
            frozenset(("丑", "戌")), frozenset(("戌", "未")), frozenset(("丑", "未")),
            frozenset(("子", "卯"))}
ZHI_PO = {frozenset(("子", "酉")), frozenset(("午", "卯")), frozenset(("申", "巳")),
          frozenset(("寅", "亥")), frozenset(("辰", "丑")), frozenset(("戌", "未"))}
ZHI_HAI = {frozenset(("子", "未")), frozenset(("丑", "午")), frozenset(("寅", "巳")),
           frozenset(("卯", "辰")), frozenset(("申", "亥")), frozenset(("酉", "戌"))}
ZHI_WONJIN = {frozenset(("子", "未")), frozenset(("丑", "午")), frozenset(("寅", "酉")),
              frozenset(("卯", "申")), frozenset(("辰", "亥")), frozenset(("巳", "戌"))}
ZHI_GWIMUN = {frozenset(("子", "酉")), frozenset(("丑", "午")), frozenset(("寅", "未")),
              frozenset(("卯", "申")), frozenset(("辰", "亥")), frozenset(("巳", "戌"))}

PILLAR_LABELS = {"year": "年", "month": "月", "day": "日", "time": "時"}
MONTH_LABELS_KO = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]

# 납음 5행 60갑자 분류 (요약)
NAYIN_KO = {
    "海中金": "해중금", "炉中火": "노중화", "大林木": "대림목", "路旁土": "노방토",
    "剑锋金": "검봉금", "山头火": "산두화", "涧下水": "간하수", "城头土": "성두토",
    "白蜡金": "백랍금", "杨柳木": "양류목", "井泉水": "정천수", "屋上土": "옥상토",
    "霹雳火": "벽력화", "松柏木": "송백목", "长流水": "장류수", "砂中金": "사중금",
    "山下火": "산하화", "平地木": "평지목", "壁上土": "벽상토", "金箔金": "금박금",
    "覆灯火": "복등화", "天河水": "천하수", "大驿土": "대역토", "钗钏金": "차천금",
    "桑柘木": "상자목", "大溪水": "대계수", "沙中土": "사중토", "天上火": "천상화",
    "石榴木": "석류목", "大海水": "대해수",
}

# 신살 한자 → 한글 (대표적인 것만)
SHEN_SHA_KO = {
    "天乙贵人": "천을귀인", "太极贵人": "태극귀인", "天德贵人": "천덕귀인",
    "月德贵人": "월덕귀인", "天德合": "천덕합", "月德合": "월덕합",
    "文昌贵人": "문창귀인", "国印贵人": "국인귀인", "学堂": "학당",
    "驿马": "역마", "桃花": "도화", "将星": "장성", "华盖": "화개",
    "金舆": "금여", "六厄": "육액", "孤辰": "고진", "寡宿": "과숙",
    "亡神": "망신", "劫煞": "겁살", "灾煞": "재살", "天煞": "천살",
    "月煞": "월살", "六害": "육해", "羊刃": "양인", "飞刃": "비인",
    "天罗": "천라", "地网": "지망", "勾绞": "구교", "披麻": "피마",
    "白虎": "백호", "丧门": "상문", "吊客": "조객", "天医": "천의",
    "禄神": "녹신", "红艳": "홍염", "金神": "금신",
}

# ── 한국 사주 핵심 신살 결정론 룰 ──
# (출처: 표준 한국 사주명리학 — 만세력 사이트들도 동일 룰)

# 천을귀인 — 일간 기준 두 개 지지
TIANYI_GUIREN = {
    "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
    "乙": ["子", "申"], "己": ["子", "申"],
    "丙": ["亥", "酉"], "丁": ["亥", "酉"],
    "辛": ["寅", "午"],
    "壬": ["巳", "卯"], "癸": ["巳", "卯"],
}

# 문창귀인 — 일간 기준 한 지지
WENCHANG_GUIREN = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯",
}

# 양인 — 일간 기준 한 지지
YANGREN = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}

# 삼합 그룹 (역마·도화·화개 계산용)
# 인오술/신자진/사유축/해묘미
SANHAP = {
    "寅": "寅午戌", "午": "寅午戌", "戌": "寅午戌",
    "申": "申子辰", "子": "申子辰", "辰": "申子辰",
    "巳": "巳酉丑", "酉": "巳酉丑", "丑": "巳酉丑",
    "亥": "亥卯未", "卯": "亥卯未", "未": "亥卯未",
}
# 역마 = 삼합 첫글자의 충
YIMA_BY_GROUP = {"寅午戌": "申", "申子辰": "寅", "巳酉丑": "亥", "亥卯未": "巳"}
# 도화 = 삼합 첫글자의 자오묘유 매칭
DOHWA_BY_GROUP = {"寅午戌": "卯", "申子辰": "酉", "巳酉丑": "午", "亥卯未": "子"}
# 화개 = 삼합 마지막
HWAGAE_BY_GROUP = {"寅午戌": "戌", "申子辰": "辰", "巳酉丑": "丑", "亥卯未": "未"}
# 장성 = 삼합 가운데 (자오묘유)
JANGSEONG_BY_GROUP = {"寅午戌": "午", "申子辰": "子", "巳酉丑": "酉", "亥卯未": "卯"}


def calc_korean_shensha(day_gan: str, year_zhi: str, day_zhi: str,
                        all_zhi: list[str]) -> dict[str, list[str]]:
    """한국 사주 핵심 신살 — 일간/년지/일지 기준 룰."""
    result = {
        "천을귀인": [], "문창귀인": [], "양인": [],
        "역마": [], "도화": [], "화개": [], "장성": [],
    }
    # 천을귀인 (일간 기준)
    for zhi in all_zhi:
        if zhi in TIANYI_GUIREN.get(day_gan, []):
            result["천을귀인"].append(f"{zhi}({ZHI_KO[zhi]})")
    # 문창귀인 (일간 기준)
    wc = WENCHANG_GUIREN.get(day_gan)
    if wc:
        for zhi in all_zhi:
            if zhi == wc:
                result["문창귀인"].append(f"{zhi}({ZHI_KO[zhi]})")
    # 양인 (일간 기준)
    yr = YANGREN.get(day_gan)
    if yr:
        for zhi in all_zhi:
            if zhi == yr:
                result["양인"].append(f"{zhi}({ZHI_KO[zhi]})")
    # 역마/도화/화개/장성 — 년지·일지 두 가지 기준 다 체크
    for base_label, base_zhi in [("년지", year_zhi), ("일지", day_zhi)]:
        if base_zhi == "?":
            continue
        group = SANHAP.get(base_zhi)
        if not group:
            continue
        ym = YIMA_BY_GROUP[group]
        dh = DOHWA_BY_GROUP[group]
        hg = HWAGAE_BY_GROUP[group]
        js = JANGSEONG_BY_GROUP[group]
        for zhi in all_zhi:
            if zhi == ym and f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)" not in result["역마"]:
                result["역마"].append(f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)")
            if zhi == dh and f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)" not in result["도화"]:
                result["도화"].append(f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)")
            if zhi == hg and f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)" not in result["화개"]:
                result["화개"].append(f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)")
            if zhi == js and f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)" not in result["장성"]:
                result["장성"].append(f"{zhi}({ZHI_KO[zhi]}, {base_label} 기준)")
    return result


CITY_LONGITUDE = {
    "seoul": 126.978, "서울": 126.978, "busan": 129.075, "부산": 129.075,
    "incheon": 126.705, "인천": 126.705, "daegu": 128.601, "대구": 128.601,
    "daejeon": 127.385, "대전": 127.385, "gwangju": 126.851, "광주": 126.851,
    "suwon": 127.029, "수원": 127.029, "jeju": 126.529, "제주": 126.529,
    "tokyo": 139.692, "도쿄": 139.692, "osaka": 135.502, "오사카": 135.502,
    "beijing": 116.407, "베이징": 116.407, "shanghai": 121.474, "상하이": 121.474,
}

KST_STANDARD_MERIDIAN = 135.0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="사주 8자 + 대운/세운/신살 계산")
    p.add_argument("--date", required=True, help="양력 생년월일 (YYYY-MM-DD)")
    p.add_argument("--time", default="12:00", help="출생 시간 (HH:MM) 또는 'unknown'")
    p.add_argument("--gender", required=True, choices=["male", "female", "남", "여"],
                   help="성별 (대운 계산 필수)")
    p.add_argument("--place", default="", help='출생지 (예: "Seoul")')
    p.add_argument("--longitude", type=float, help="경도 (--place 대신)")
    p.add_argument("--true-solar", action="store_true", help="진태양시 보정")
    p.add_argument("--output", default=None, help="결과 .md 경로")
    p.add_argument("--print-only", action="store_true", help="파일 갱신 안 함")
    p.add_argument("--liunian-years", type=int, default=10, help="세운 표시 년수 (기본 10년)")
    return p.parse_args()


def resolve_longitude(place, longitude):
    if longitude is not None:
        return longitude
    if not place:
        return None
    return CITY_LONGITUDE.get(place.split(",")[0].strip().lower())


def apply_true_solar(dt, longitude):
    delta = (longitude - KST_STANDARD_MERIDIAN) * 4
    return dt + timedelta(minutes=delta)


def to_ko(text):
    """한자 → 한글 변환 (매핑 있는 것만, 없으면 원문)."""
    if not text:
        return ""
    # SHEN_SHA + DISHI + SHISHEN + NAYIN 일괄 치환
    out = text
    for k, v in {**SHEN_SHA_KO, **DISHI_KO, **SHISHEN_KO, **NAYIN_KO}.items():
        out = out.replace(k, f"{v}({k})")
    return out


def fmt_zhushishen(items):
    """지지 십신 list → 한글."""
    if not items:
        return "-"
    return ", ".join(f"{SHISHEN_KO.get(s, s)}" for s in items)


def fmt_hidegan(items):
    if not items:
        return "-"
    return ", ".join(f"{g}({GAN_KO.get(g, g)})" for g in items)


def fmt_shensha_list(items):
    if not items:
        return "-"
    return ", ".join(SHEN_SHA_KO.get(s, s) for s in items)


def gan_zhi(ganzhi: str) -> tuple[str, str]:
    return (ganzhi[0], ganzhi[1]) if len(ganzhi) >= 2 else ("?", "?")


def shishen_ko_for_gan(day_gan: str, gan: str) -> str:
    if gan == "?" or day_gan == "?":
        return "-"
    raw = TEN_GOD_BY_DAY_STEM.get(day_gan, {}).get(gan, "")
    return SHISHEN_KO.get(raw, raw) or "-"


def shishen_ko_for_zhi(day_gan: str, zhi: str) -> str:
    if zhi == "?" or day_gan == "?":
        return "-"
    hidden = BRANCH_HIDDEN_MAIN.get(zhi)
    return shishen_ko_for_gan(day_gan, hidden) if hidden else "-"


BRANCH_HIDDEN_MAIN = {
    "子": "癸", "丑": "己", "寅": "甲", "卯": "乙", "辰": "戊", "巳": "丙",
    "午": "丁", "未": "己", "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬",
}


def relation_detail(label_a: str, zhi_a: str, label_b: str, zhi_b: str, kind: str, element=None) -> str:
    elem = f" → {WUXING_KO.get(element, element)}" if element else ""
    return f"{label_a}{zhi_a}{label_b}{zhi_b} {kind}{elem}"


def calc_relations(pillars: dict[str, tuple[str, str]]) -> dict:
    """원국 내 천간/지지 관계. 해석 확정이 아니라 LLM 해석 재료."""
    keys = ["year", "month", "day", "time"]
    stem_relations = []
    branch_relations: dict[str, list[str]] = {
        "방합": [], "삼합": [], "반합": [], "육합": [], "충": [], "형": [], "파": [], "해": [], "원진": [], "귀문": []
    }

    present = [(k, pillars[k][0], pillars[k][1]) for k in keys if pillars[k][0] != "?" and pillars[k][1] != "?"]

    for i, (ka, ga, za) in enumerate(present):
        for kb, gb, zb in present[i + 1:]:
            labels = (PILLAR_LABELS[ka], PILLAR_LABELS[kb])
            pair_g = frozenset((ga, gb))
            if pair_g in GAN_HAP:
                stem_relations.append(f"{labels[0]}{ga}{labels[1]}{gb} 천간합 → {WUXING_KO[GAN_HAP[pair_g]]}")
            if pair_g in GAN_CHONG:
                stem_relations.append(f"{labels[0]}{ga}{labels[1]}{gb} 천간충")

            pair_z = frozenset((za, zb))
            if pair_z in ZHI_LIUHE:
                branch_relations["육합"].append(relation_detail(labels[0], za, labels[1], zb, "육합", ZHI_LIUHE[pair_z]))
            if pair_z in ZHI_BANHE:
                branch_relations["반합"].append(relation_detail(labels[0], za, labels[1], zb, "반합", ZHI_BANHE[pair_z]))
            if pair_z in ZHI_CHONG:
                branch_relations["충"].append(relation_detail(labels[0], za, labels[1], zb, "충"))
            if pair_z in ZHI_XING:
                branch_relations["형"].append(relation_detail(labels[0], za, labels[1], zb, "형"))
            if pair_z in ZHI_PO:
                branch_relations["파"].append(relation_detail(labels[0], za, labels[1], zb, "파"))
            if pair_z in ZHI_HAI:
                branch_relations["해"].append(relation_detail(labels[0], za, labels[1], zb, "해"))
            if pair_z in ZHI_WONJIN:
                branch_relations["원진"].append(relation_detail(labels[0], za, labels[1], zb, "원진"))
            if pair_z in ZHI_GWIMUN:
                branch_relations["귀문"].append(relation_detail(labels[0], za, labels[1], zb, "귀문"))

    present_zhi = {z for _, _, z in present}
    for group, elem in ZHI_SANHE.items():
        if group.issubset(present_zhi):
            branch_relations["삼합"].append(f"{''.join(group)} 삼합 → {WUXING_KO[elem]}")
    for group, elem in ZHI_FANGHE.items():
        if group.issubset(present_zhi):
            branch_relations["방합"].append(f"{''.join(group)} 방합 → {WUXING_KO[elem]}")

    return {"stem": stem_relations, "branch": branch_relations}


def relation_priorities(relations: dict) -> list[dict[str, str | float]]:
    rules = [
        ("충", 5.0, "급변·충돌 가능성"),
        ("형", 4.5, "압박·피로 누적 가능성"),
        ("파", 3.5, "관계 균열·계획 변동 가능성"),
        ("해", 3.0, "오해·소통 불일치 가능성"),
        ("원진", 2.8, "감정적 피로 누적 가능성"),
        ("귀문", 2.8, "심리적 예민함·내적 갈등 가능성"),
        ("삼합", 2.6, "기운 결집·확장 포인트"),
        ("방합", 2.4, "방향성·세력화 포인트"),
        ("육합", 2.2, "협력·완충 포인트"),
        ("반합", 1.8, "조건부 협력 포인트"),
    ]
    items: list[dict[str, str | float]] = []
    for text in relations["stem"]:
        if "천간충" in text:
            items.append({"label": "천간 충", "score": 4.8, "note": "의사결정·대인 충돌 가능성", "detail": text})
        elif "천간합" in text:
            items.append({"label": "천간 합", "score": 2.0, "note": "완충·협력 가능성", "detail": text})
    for key, weight, note in rules:
        for text in relations["branch"][key]:
            items.append({"label": f"지지 {key}", "score": weight, "note": note, "detail": text})
    return sorted(items, key=lambda x: (-float(x["score"]), str(x["label"])))


def calc_advanced(day_gan: str, month_zhi: str, wuxing_count: dict[str, int], shishen_gan: dict[str, str]) -> dict:
    """격국·용신 참고값. 유파 차이가 커서 확정값이 아닌 해석 보조로만 사용."""
    day_elem = GAN_WUXING[day_gan]
    support = wuxing_count[day_elem] + wuxing_count[ELEMENT_GENERATED_BY[day_elem]]
    drain = wuxing_count[ELEMENT_GENERATES[day_elem]]
    pressure = wuxing_count[ELEMENT_CONTROLLED_BY[day_elem]]
    wealth = wuxing_count[ELEMENT_CONTROLS[day_elem]]
    score = support * 18 - (drain + pressure + wealth) * 8
    if month_zhi and ZHI_WUXING.get(month_zhi) == day_elem:
        score += 20
    strength = "강" if score >= 35 else "약" if score <= 5 else "중간"

    month_ten_god = shishen_gan.get("month", "")
    geukguk = f"{SHISHEN_KO.get(month_ten_god, month_ten_god)}격 참고" if month_ten_god else "격국 참고 필요"

    if strength == "강":
        candidates = [ELEMENT_GENERATES[day_elem], ELEMENT_CONTROLLED_BY[day_elem], ELEMENT_CONTROLS[day_elem]]
        note = "일간이 강한 편으로 보면 설기·관성·재성 쪽 균형을 우선 검토"
    elif strength == "약":
        candidates = [ELEMENT_GENERATED_BY[day_elem], day_elem]
        note = "일간이 약한 편으로 보면 인성·비겁 쪽 보강을 우선 검토"
    else:
        candidates = [ELEMENT_GENERATES[day_elem], ELEMENT_GENERATED_BY[day_elem]]
        note = "중간 강도로 보면 과다·부족 오행과 월지를 함께 재검토"

    return {
        "day_strength": strength,
        "day_strength_score": score,
        "geukguk": geukguk,
        "yongsin_candidates": [WUXING_KO[e] for e in candidates],
        "note": note,
    }


def build_compact_summary(r: dict) -> str:
    pillars = r["pillars"]
    day_gan = r["day_master"]
    wx = r["wuxing_count"]
    ss = r["shishen_groups"]
    advanced = r["advanced"]
    relation_top = r["relation_priorities"][:5]
    relation_line = " / ".join(f"{i+1}.{x['label']} {x['detail']}" for i, x in enumerate(relation_top)) or "강한 관계 신호 없음"
    daeyun_line = " / ".join(f"{d['start_age']}~{d['end_age']} {d['ganzhi']}" for d in r["da_yun"][:5])
    seyun_line = " / ".join(f"{x['year']} {x['ganzhi']}({x['gan_ten_god']}/{x['zhi_ten_god']})" for x in r["liu_nian"][:6])

    return "\n".join([
        "## LLM 압축 요약",
        f"원국 年{''.join(pillars['year'])} 月{''.join(pillars['month'])} 日{''.join(pillars['day'])} 時{''.join(pillars['time'])}",
        f"일간 {day_gan}({GAN_KO[day_gan]}){WUXING_KO[GAN_WUXING[day_gan]]} / 강약 참고 {advanced['day_strength']}({advanced['day_strength_score']}) / 격국 {advanced['geukguk']} / 용신 후보 {', '.join(advanced['yongsin_candidates'])}",
        f"오행 목{wx['木']} 화{wx['火']} 토{wx['土']} 금{wx['金']} 수{wx['水']} / 십신 비겁{ss['비겁']} 식상{ss['식상']} 재성{ss['재성']} 관성{ss['관성']} 인성{ss['인성']}",
        f"관계 우선순위: {relation_line}",
        f"대운: {daeyun_line}",
        f"세운: {seyun_line}",
    ])


def calculate(args):
    # 날짜·시간 파싱
    date_part = datetime.strptime(args.date, "%Y-%m-%d")
    time_known = args.time.lower() != "unknown"
    if time_known:
        t = datetime.strptime(args.time, "%H:%M")
        dt_input = date_part.replace(hour=t.hour, minute=t.minute)
    else:
        dt_input = date_part.replace(hour=12, minute=0)

    # 진태양시
    dt_corrected = None
    if args.true_solar:
        lon = resolve_longitude(args.place, args.longitude)
        if lon is None:
            raise ValueError(f"진태양시 보정용 경도 미상: place={args.place}")
        dt_corrected = apply_true_solar(dt_input, lon)
        dt_used = dt_corrected
    else:
        dt_used = dt_input

    solar = Solar.fromYmdHms(dt_used.year, dt_used.month, dt_used.day,
                              dt_used.hour, dt_used.minute, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()

    # 8자 — lunar-python
    pillars = {
        "year": (ec.getYearGan(), ec.getYearZhi()),
        "month": (ec.getMonthGan(), ec.getMonthZhi()),
        "day": (ec.getDayGan(), ec.getDayZhi()),
        "time": (ec.getTimeGan(), ec.getTimeZhi()) if time_known else ("?", "?"),
    }

    # 8자 — sajupy (한국 만세력 검증용, primary 출처)
    # 진태양시 보정은 calc_saju.py에서 이미 수행했으므로 sajupy에서는 OFF
    sajupy_result = sajupy_calculate(
        year=dt_used.year, month=dt_used.month, day=dt_used.day,
        hour=dt_used.hour, minute=dt_used.minute,
        use_solar_time=False,
    )
    sajupy_pillars = {
        "year": (sajupy_result["year_stem"], sajupy_result["year_branch"]),
        "month": (sajupy_result["month_stem"], sajupy_result["month_branch"]),
        "day": (sajupy_result["day_stem"], sajupy_result["day_branch"]),
        "time": (sajupy_result["hour_stem"], sajupy_result["hour_branch"]) if time_known else ("?", "?"),
    }

    # 자동 cross-check
    mismatches = []
    for k in ["year", "month", "day", "time"]:
        if pillars[k] != sajupy_pillars[k]:
            mismatches.append({
                "pillar": k,
                "lunar_python": f"{pillars[k][0]}{pillars[k][1]}",
                "sajupy": f"{sajupy_pillars[k][0]}{sajupy_pillars[k][1]}",
            })
    if mismatches:
        sys.stderr.write("\n" + "=" * 70 + "\n")
        sys.stderr.write("🚨 한국 만세력(sajupy) ↔ lunar-python 불일치 감지!\n")
        sys.stderr.write("=" * 70 + "\n")
        for mm in mismatches:
            sys.stderr.write(f"  {mm['pillar']}: lunar-py={mm['lunar_python']}  sajupy={mm['sajupy']}\n")
        sys.stderr.write("\n진행 중단. 출생 정보 확인 또는 라이브러리 버그 보고 필요.\n")
        sys.stderr.write("=" * 70 + "\n")
        sys.exit(2)

    # 오행 카운트
    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for gan, zhi in pillars.values():
        if gan != "?":
            wuxing_count[GAN_WUXING[gan]] += 1
        if zhi != "?":
            wuxing_count[ZHI_WUXING[zhi]] += 1

    # 십신 (천간 + 지지)
    shishen_gan = {
        "year": ec.getYearShiShenGan(),
        "month": ec.getMonthShiShenGan(),
        "time": ec.getTimeShiShenGan() if time_known else "?",
    }
    shishen_zhi = {
        "year": ec.getYearShiShenZhi(),
        "month": ec.getMonthShiShenZhi(),
        "day": ec.getDayShiShenZhi(),
        "time": ec.getTimeShiShenZhi() if time_known else [],
    }

    # 십신 그룹 카운트
    ss_groups = {"비겁": 0, "식상": 0, "재성": 0, "관성": 0, "인성": 0}
    for s in shishen_gan.values():
        if s in SHISHEN_GROUPS:
            ss_groups[SHISHEN_GROUPS[s]] += 1
    for items in shishen_zhi.values():
        for s in items if isinstance(items, list) else []:
            if s in SHISHEN_GROUPS:
                ss_groups[SHISHEN_GROUPS[s]] += 1

    # 12운성
    dishi = {
        "year": ec.getYearDiShi(),
        "month": ec.getMonthDiShi(),
        "day": ec.getDayDiShi(),
        "time": ec.getTimeDiShi() if time_known else "?",
    }

    # 공망
    xunkong = {
        "year": ec.getYearXunKong(),
        "month": ec.getMonthXunKong(),
        "day": ec.getDayXunKong(),
        "time": ec.getTimeXunKong() if time_known else "?",
    }

    # 납음
    nayin = {
        "year": ec.getYearNaYin(),
        "month": ec.getMonthNaYin(),
        "day": ec.getDayNaYin(),
        "time": ec.getTimeNaYin() if time_known else "?",
    }

    # 지장간
    hidegan = {
        "year": ec.getYearHideGan(),
        "month": ec.getMonthHideGan(),
        "day": ec.getDayHideGan(),
        "time": ec.getTimeHideGan() if time_known else [],
    }

    # 신살 (lunar-python 일진 기반)
    ji_shen = lunar.getDayJiShen() or []
    xiong_sha = lunar.getDayXiongSha() or []

    # 한국 사주 핵심 신살 (천을귀인/문창/양인/역마/도화/화개/장성)
    all_zhi_for_shensha = [pillars["year"][1], pillars["month"][1],
                            pillars["day"][1], pillars["time"][1]]
    all_zhi_for_shensha = [z for z in all_zhi_for_shensha if z != "?"]
    korean_shensha = calc_korean_shensha(
        day_gan=pillars["day"][0],
        year_zhi=pillars["year"][1],
        day_zhi=pillars["day"][1],
        all_zhi=all_zhi_for_shensha,
    )
    relations = calc_relations(pillars)
    rel_priorities = relation_priorities(relations)
    advanced = calc_advanced(
        day_gan=pillars["day"][0],
        month_zhi=pillars["month"][1],
        wuxing_count=wuxing_count,
        shishen_gan=shishen_gan,
    )

    # 명궁/태원/태식
    extras = {
        "ming_gong": ec.getMingGong(),
        "tai_yuan": ec.getTaiYuan(),
        "tai_xi": ec.getTaiXi(),
    }

    # 대운
    gender_val = 1 if args.gender in ("male", "남") else 0
    yun = ec.getYun(gender_val)
    da_yun_list = []
    for d in yun.getDaYun()[:9]:  # 첫 9개 (대략 0~80세)
        da_yun_list.append({
            "start_age": d.getStartAge(),
            "end_age": d.getEndAge(),
            "start_year": d.getStartYear(),
            "end_year": d.getEndYear(),
            "ganzhi": d.getGanZhi(),
        })

    yun_meta = {
        "start_solar": yun.getStartSolar().toYmd(),
        "start_year_offset": yun.getStartYear(),
        "start_month_offset": yun.getStartMonth(),
        "start_day_offset": yun.getStartDay(),
        "is_forward": yun.isForward(),
    }

    # 세운 (현재 진행 중인 대운 + 다음 N년)
    current_year = datetime.now().year
    liu_nian_list = []
    wolun_list = []
    for d in yun.getDaYun():
        if d.getStartYear() <= current_year <= d.getEndYear():
            for ln in d.getLiuNian():
                if current_year <= ln.getYear() <= current_year + args.liunian_years - 1:
                    ln_gan, ln_zhi = gan_zhi(ln.getGanZhi())
                    liu_nian_list.append({
                        "year": ln.getYear(),
                        "ganzhi": ln.getGanZhi(),
                        "gan_ten_god": shishen_ko_for_gan(pillars["day"][0], ln_gan),
                        "zhi_ten_god": shishen_ko_for_zhi(pillars["day"][0], ln_zhi),
                        "age": ln.getYear() - args.liunian_years + (d.getEndAge() - d.getStartAge()),
                    })
                    if ln.getYear() == current_year:
                        for ly in ln.getLiuYue()[:12]:
                            ly_gan, ly_zhi = gan_zhi(ly.getGanZhi())
                            idx = ly.getIndex()
                            wolun_list.append({
                                "month": MONTH_LABELS_KO[idx] if 0 <= idx < 12 else ly.getMonthInChinese(),
                                "ganzhi": ly.getGanZhi(),
                                "gan_ten_god": shishen_ko_for_gan(pillars["day"][0], ly_gan),
                                "zhi_ten_god": shishen_ko_for_zhi(pillars["day"][0], ly_zhi),
                            })
            # 현재 대운 다음 대운까지 확장
            next_idx = d.getIndex() + 1
            all_dy = yun.getDaYun()
            if next_idx < len(all_dy):
                for ln in all_dy[next_idx].getLiuNian():
                    if len(liu_nian_list) >= args.liunian_years:
                        break
                    if current_year <= ln.getYear() <= current_year + args.liunian_years - 1:
                        ln_gan, ln_zhi = gan_zhi(ln.getGanZhi())
                        liu_nian_list.append({
                            "year": ln.getYear(),
                            "ganzhi": ln.getGanZhi(),
                            "gan_ten_god": shishen_ko_for_gan(pillars["day"][0], ln_gan),
                            "zhi_ten_god": shishen_ko_for_zhi(pillars["day"][0], ln_zhi),
                            "age": None,
                        })
            break

    result = {
        "pillars": pillars,
        "wuxing_count": wuxing_count,
        "shishen_gan": shishen_gan,
        "shishen_zhi": shishen_zhi,
        "shishen_groups": ss_groups,
        "dishi": dishi,
        "xunkong": xunkong,
        "nayin": nayin,
        "hidegan": hidegan,
        "ji_shen": ji_shen,
        "xiong_sha": xiong_sha,
        "korean_shensha": korean_shensha,
        "relations": relations,
        "relation_priorities": rel_priorities,
        "advanced": advanced,
        "extras": extras,
        "yun_meta": yun_meta,
        "da_yun": da_yun_list,
        "liu_nian": liu_nian_list,
        "wolun": wolun_list,
        "current_year": current_year,
        "lunar_date": f"{lunar.getYear()}-{lunar.getMonth():02d}-{lunar.getDay():02d}",
        "day_master": pillars["day"][0],
        "time_known": time_known,
        "dt_input": dt_input,
        "dt_corrected": dt_corrected,
    }
    result["compact_summary"] = build_compact_summary(result)
    return result


def fmt_pillar(gan, zhi):
    if gan == "?":
        return ("?", "?")
    return (
        f"{gan}({GAN_KO[gan]}, {WUXING_KO[GAN_WUXING[gan]]})",
        f"{zhi}({ZHI_KO[zhi]}, {WUXING_KO[ZHI_WUXING[zhi]]})",
    )


def render_md(args, r):
    pillars = r["pillars"]
    wx = r["wuxing_count"]
    ss = r["shishen_groups"]

    yg, yz = fmt_pillar(*pillars["year"])
    mg, mz = fmt_pillar(*pillars["month"])
    dg, dz = fmt_pillar(*pillars["day"])
    tg, tz = fmt_pillar(*pillars["time"])

    def strength(n):
        if n == 0: return "없음 (부족)"
        if n == 1: return "약함"
        if n == 2: return "보통"
        if n == 3: return "강함"
        return "과다"

    over = [WUXING_KO[k] for k, v in wx.items() if v >= 3]
    under = [WUXING_KO[k] for k, v in wx.items() if v == 0]

    place_str = args.place or "(미지정)"
    true_solar_str = "적용" if args.true_solar and r["dt_corrected"] else "미적용"
    gender_ko = "남" if args.gender in ("male", "남") else "여"

    day_master_ko = (f"{r['day_master']}({GAN_KO[r['day_master']]}, "
                     f"{WUXING_KO[GAN_WUXING[r['day_master']]]})")

    # 12운성 행
    dishi_row = " | ".join(
        DISHI_KO.get(r["dishi"][k], r["dishi"][k]) + f"({r['dishi'][k]})" if r["dishi"][k] != "?" else "?"
        for k in ["year", "month", "day", "time"]
    )

    # 공망 행
    xk_row = " | ".join(r["xunkong"][k] if r["xunkong"][k] != "?" else "?"
                       for k in ["year", "month", "day", "time"])

    # 납음 행
    ny_row = " | ".join(
        NAYIN_KO.get(r["nayin"][k], r["nayin"][k]) + f"({r['nayin'][k]})" if r["nayin"][k] != "?" else "?"
        for k in ["year", "month", "day", "time"]
    )

    # 지장간 행
    hg_row = " | ".join(fmt_hidegan(r["hidegan"][k]) for k in ["year", "month", "day", "time"])

    # 십신 (천간) 행 — 일간 자기 자신 빼고
    ssg_row_parts = []
    for k in ["year", "month", "day", "time"]:
        if k == "day":
            ssg_row_parts.append("(일간)")
        else:
            v = r["shishen_gan"][k]
            ssg_row_parts.append(SHISHEN_KO.get(v, v) if v != "?" else "?")
    ssg_row = " | ".join(ssg_row_parts)

    # 십신 (지지) 행
    ssz_row = " | ".join(fmt_zhushishen(r["shishen_zhi"][k]) for k in ["year", "month", "day", "time"])

    # 대운 표
    da_yun_rows = "\n".join(
        f"| {d['start_age']:>2}~{d['end_age']:>2}세 | {d['start_year']}~{d['end_year']} | {d['ganzhi']} |"
        for d in r["da_yun"]
    )

    # 세운 표 (현재 + N년)
    if r["liu_nian"]:
        liu_nian_rows = "\n".join(
            f"| {ln['year']} | {ln['ganzhi']} | {ln['gan_ten_god']} | {ln['zhi_ten_god']} |" for ln in r["liu_nian"]
        )
    else:
        liu_nian_rows = "| (계산 불가) | - | - | - |"

    # 월운 표 (올해 12개월)
    if r["wolun"]:
        wolun_rows = "\n".join(
            f"| {w['month']} | {w['ganzhi']} | {w['gan_ten_god']} | {w['zhi_ten_god']} |" for w in r["wolun"]
        )
    else:
        wolun_rows = "| (계산 불가) | - | - | - |"

    # 관계 강도 표
    if r["relation_priorities"]:
        relation_rows = "\n".join(
            f"| {i + 1} | {item['label']} | {float(item['score']):.1f} | {item['detail']} | {item['note']} |"
            for i, item in enumerate(r["relation_priorities"])
        )
    else:
        relation_rows = "| - | 특이 신호 없음 | - | - | 충/형 중심의 강한 충돌 신호는 상대적으로 약함 |"

    branch_relation_lines = []
    for key, items in r["relations"]["branch"].items():
        if items:
            branch_relation_lines.append(f"- **{key}**: " + " / ".join(items))
    branch_relation_block = "\n".join(branch_relation_lines) if branch_relation_lines else "- 특이 지지 관계 없음"
    stem_relation_block = "\n".join(f"- {x}" for x in r["relations"]["stem"]) if r["relations"]["stem"] else "- 특이 천간 관계 없음"

    yun_dir = "순행 (양남/음녀)" if r["yun_meta"]["is_forward"] else "역행 (음남/양녀)"
    advanced = r["advanced"]

    md = f"""# 사주 — 8자 + 대운 + 세운 + 신살 + 12운성 + 공망

> 양력 생년월일시 + 성별 → 결정론적 계산.
> **검증된 출처:** 8자 = sajupy (한국 만세력 1900-2100) ↔ lunar-python (자동 cross-check 통과 ✅)
> 추가 기능 = lunar-python (대운/세운/12운성/공망/신살/지장간/납음)
> **계산은 박제, 해석은 on-demand.** LLM 추측 ❌.

---

{r["compact_summary"]}

> 위 압축 요약은 다른 LLM에 `saju.md` 전체를 넣기 어려울 때 우선 전달하는 섹션.
> 단, 사주는 보조 색깔이며 실제 조언의 1순위 근거는 사용자가 직접 채운 자기진단·철학·시스템이다.

---

## 입력 정보

| 항목 | 값 |
|---|---|
| 양력 생년월일 | {args.date} |
| 출생 시간 | {args.time if r["time_known"] else "미상"} |
| 성별 | {gender_ko} |
| 출생 장소 | {place_str} |
| 음력 생년월일 | {r["lunar_date"]} |
| 진태양시 보정 | {true_solar_str} |

---

## 사주 8자

|  | 천간 | 지지 |
|---|---|---|
| 年柱 (연주) | {yg} | {yz} |
| 月柱 (월주) | {mg} | {mz} |
| 日柱 (일주) — 본인 | **{dg}** | {dz} |
| 時柱 (시주) | {tg} | {tz} |

**일간(日干) = {day_master_ko}** — 본인의 본질을 나타내는 천간.

---

## 십신 (十神) — 일간 기준 다른 7글자의 관계

|  | 年 | 月 | 日 | 時 |
|---|---|---|---|---|
| 천간 십신 | {ssg_row} |
| 지지 십신 | {ssz_row} |

**십신 그룹 분포** (천간 + 지지 합산):

| 그룹 | 개수 | 의미 |
|---|---|---|
| 비겁 (비견·겁재) | {ss['비겁']} | 자기·친구·경쟁 |
| 식상 (식신·상관) | {ss['식상']} | 표현·창의·자식·일 |
| 재성 (편재·정재) | {ss['재성']} | 돈·여자(남명)·실리·욕망 |
| 관성 (편관·정관) | {ss['관성']} | 지위·남자(여명)·압박·규율 |
| 인성 (편인·정인) | {ss['인성']} | 학문·어머니·보호·문서 |

---

## 오행 분포 (천간 + 지지)

| 오행 | 개수 | 강약 |
|---|---|---|
| 木 (목) | {wx['木']} | {strength(wx['木'])} |
| 火 (화) | {wx['火']} | {strength(wx['火'])} |
| 土 (토) | {wx['土']} | {strength(wx['土'])} |
| 金 (금) | {wx['金']} | {strength(wx['金'])} |
| 水 (수) | {wx['水']} | {strength(wx['水'])} |

**과다 오행:** {", ".join(over) or "없음"}
**부족 오행:** {", ".join(under) or "없음"}

---

## 12운성 — 일간이 각 지지를 만났을 때의 기운 강약

|  | 年 | 月 | 日 | 時 |
|---|---|---|---|---|
| 12운성 | {dishi_row} |

> 장생→목욕→관대→임관→제왕→쇠→병→사→묘→절→태→양 (12단계 순환).
> **임관·제왕** = 일간 강함 / **사·묘·절** = 일간 약함.

---

## 공망 (空亡) — 비어있는 두 지지

|  | 年 | 月 | 日 | 時 |
|---|---|---|---|---|
| 공망 | {xk_row} |

> 일주 공망이 가장 중요. 해당 지지가 사주 다른 곳에 있으면 그 영역에서 *결과 안 남는 노력*이 잦음.

---

## 납음 5행 (60갑자별 고유 5행)

|  | 年 | 月 | 日 | 時 |
|---|---|---|---|---|
| 납음 | {ny_row} |

---

## 지장간 (地藏干) — 지지에 숨은 천간

|  | 年支 | 月支 | 日支 | 時支 |
|---|---|---|---|---|
| 지장간 | {hg_row} |

> 월지 지장간 = 격국 판정의 핵심.

---

## 원국 관계 — 합·충·형·파·해·원진·귀문

### 천간 관계

{stem_relation_block}

### 지지 관계

{branch_relation_block}

### 관계 강도 우선순위

| 순위 | 관계 | 점수 | 근거 | 해석 포인트 |
|---|---|---:|---|---|
{relation_rows}

> 이 섹션은 `ssaju`식 LLM-ready 관계 요약을 참고해 추가한 해석 재료.
> 관계 자체가 운명을 결정하지 않는다. 충·형은 위험 딱지가 아니라 *미리 보는 긴장 지점*이다.

---

## 고급 분석 참고 — 일간 강약·격국·용신 후보

| 항목 | 값 |
|---|---|
| 일간 강약 참고 | {advanced["day_strength"]} ({advanced["day_strength_score"]}) |
| 격국 참고 | {advanced["geukguk"]} |
| 용신 후보 | {", ".join(advanced["yongsin_candidates"])} |
| 해석 메모 | {advanced["note"]} |

> 격국·용신은 유파 차이가 크므로 **확정값이 아니라 참고값**이다.
> 사용자가 명시 요청했을 때만 해석에 쓰고, 사용자 자기입력을 덮어쓰지 않는다.

---

## 신살 (神煞)

### 한국 사주 핵심 신살 (일간·년지·일지 기준 결정론 계산)

| 신살 | 사주 내 위치 | 의미 |
|---|---|---|
| 천을귀인 (天乙貴人) | {", ".join(r["korean_shensha"]["천을귀인"]) or "없음"} | 최강 길신, 위기 시 도움받음 |
| 문창귀인 (文昌貴人) | {", ".join(r["korean_shensha"]["문창귀인"]) or "없음"} | 학문·문서·시험·표현 |
| 양인 (羊刃) | {", ".join(r["korean_shensha"]["양인"]) or "없음"} | 강한 추진력, 과하면 사고·다툼 |
| 역마 (驛馬) | {", ".join(r["korean_shensha"]["역마"]) or "없음"} | 이동·여행·해외·변동 |
| 도화 (桃花) | {", ".join(r["korean_shensha"]["도화"]) or "없음"} | 인기·미모·이성 인연·예술 |
| 화개 (華蓋) | {", ".join(r["korean_shensha"]["화개"]) or "없음"} | 종교·예술·고독·수도 |
| 장성 (將星) | {", ".join(r["korean_shensha"]["장성"]) or "없음"} | 리더십·권위·지휘 |

### lunar-python 일진 기반 신살 (참고)

**길신 (吉神)**: {fmt_shensha_list(r["ji_shen"])}
**흉신 (凶煞)**: {fmt_shensha_list(r["xiong_sha"])}

> LLM에게 "내 신살 중 가장 중요한 거 3개 짚어줘" 요청.

---

## 명궁 / 태원 / 태식

| 항목 | 간지 | 의미 |
|---|---|---|
| 명궁 (命宮) | {r["extras"]["ming_gong"]} | 본인의 *내면 운명궁* |
| 태원 (胎元) | {r["extras"]["tai_yuan"]} | 잉태된 시점의 간지 (전생적 자질) |
| 태식 (胎息) | {r["extras"]["tai_xi"]} | 태아 시기의 호흡 (선천 기질) |

---

## 대운 (大運) — 10년 단위 인생 흐름

**대운 시작:** {r["yun_meta"]["start_solar"]} (출생 후 {r["yun_meta"]["start_year_offset"]}년 {r["yun_meta"]["start_month_offset"]}개월 {r["yun_meta"]["start_day_offset"]}일)
**대운 방향:** {yun_dir}

| 나이 | 연도 | 간지 |
|---|---|---|
{da_yun_rows}

> 본인 현재 나이가 어느 대운에 속하는지 확인 → 그 간지가 향후 10년의 *큰 흐름*.

---

## 세운 (歲運) — 향후 {args.liunian_years}년

| 연도 | 간지 | 천간 십신 | 지지 십신 |
|---|---|---|---|
{liu_nian_rows}

> 매년 들어오는 간지. 일간과의 십신 관계로 *그 해의 테마* 결정.

---

## 월운 (月運) — {r["current_year"]}년 12개월

| 월 | 간지 | 천간 십신 | 지지 십신 |
|---|---|---|---|
{wolun_rows}

> 월운은 월 단위 리듬을 보는 보조 자료. 분기·월간 계획과 연결할 때만 가볍게 참조.

---

## 해석 — 본인 기질 한 줄 요약

<!-- LLM이 위 데이터 전부 기반으로 작성. 매년 갱신 가능. -->
<!-- AI에게: "내 사주 8자/십신/12운성/대운/신살 종합해서 한 줄 요약해줘" 요청 -->

> (해석 필요)

---

## 강한 영역 (사주가 받쳐주는 곳)

(LLM에게 "내 사주에서 강한 영역 3개 알려줘" 요청)

## 약한 영역 (사주가 안 받쳐주는 곳 — 시스템으로 보완)

(LLM에게 "내 사주에서 약한 영역 3개 알려줘" 요청)

---

## 활용 — 다른 문서와 연결

- 사주 강한 영역 → [philosophy.md](philosophy.md) *3개 축* 검증
- 사주 약한 영역 → [life_os.md](life_os.md) *6 레이어*로 보완
- 대운/세운 → [roadmap.md](roadmap.md) *연간/분기* 목표와 매칭

---

## 한 줄

> **사주는 *기본 토양*. 시스템은 *작물*. 토양 알면 어떤 작물 잘 자라는지 보임.**
> 사주가 운명 결정 ❌. 약한 곳은 시스템(life_os)으로 보완.

---

## 갱신 이력

- {datetime.now().strftime("%Y-%m-%d")}: `scripts/calc_saju.py` 실행 (8자 + 십신 + 12운성 + 공망 + 납음 + 지장간 + 신살 + 관계 강도 + 대운 + 세운 + 월운)
"""
    return md


def main():
    args = parse_args()
    try:
        r = calculate(args)
    except Exception as e:
        sys.stderr.write(f"계산 실패: {e}\n")
        return 1

    pillars = r["pillars"]
    print(f"양력: {args.date} {args.time} ({args.gender}, {args.place or '미지정'})")
    print(f"음력: {r['lunar_date']}")
    if r["dt_corrected"]:
        print(f"진태양시: {r['dt_input'].strftime('%H:%M')} → {r['dt_corrected'].strftime('%H:%M')}")
    print()
    print("8자:")
    for k, label in [("year", "年"), ("month", "月"), ("day", "日"), ("time", "時")]:
        g, z = pillars[k]
        marker = "  ← 일간" if k == "day" else ""
        print(f"  {label}柱: {g}{z}{marker}")
    print()
    print("오행:", " ".join(f"{k}({v})" for k, v in r["wuxing_count"].items()))
    print(f"십신 그룹: {r['shishen_groups']}")
    print(f"공망(일주): {r['xunkong']['day']}")
    print(f"12운성(일주): {r['dishi']['day']}")
    print(f"신살 길신: {len(r['ji_shen'])}개  흉신: {len(r['xiong_sha'])}개")
    print(f"대운: {len(r['da_yun'])}개  세운: {len(r['liu_nian'])}개")

    if args.print_only:
        return 0

    output = Path(args.output) if args.output else (
        Path(__file__).parent.parent / "templates" / "saju.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_md(args, r), encoding="utf-8")
    print(f"\n✅ 저장됨: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
