#!/usr/bin/env python3
"""Tool 10: GL34分红保单治理合规检查 (gl34_compliance_check)

GL34 《指引34—分红业务管治指引》2026-03-31生效
Section 4 公司政策要求 2026-06-30前完成

与 compliance_check (Tool 2) 并行运行，专注分红保单治理规则。
"""
import re
from typing import Dict, Any, List
import os

# ========== GL34 Rules (6条) ==========

GL34_RULES = [
    {
        "rule_id": "GL34-001",
        "name": "PBC结构要求检查",
        "trigger_patterns": r"(分红保险|participating.*policy|redistribut.*fund|分红基金)",
        "check_fn": None,  # regex-based: PBC must be mentioned when分红 product discussed
        "yellow_pattern": r"(?!(?(?=.*[管治委员会|治理委员会|PBC|独立监督|Board oversight]).*))",
        "severity": "YELLOW_LINE",
        "description": "讨论分红产品时，必须提及独立PBC管治框架",
        "regulatory_ref": "GL34 §2.1 — Participating Policy Committee",
    },
    {
        "rule_id": "GL34-002",
        "name": "基金资产隔离声明",
        "trigger_patterns": r"(回报|收益|dividend.*return|fund.*performance|分红表现|资产增值)",
        "check_fn": None,
        "severity": "YELLOW_LINE",
        "description": "讨论回报时必须声明保单基金与股东资产分离管理",
        "regulatory_ref": "GL34 §2.3 — Fund Asset Isolation",
    },
    {
        "rule_id": "GL34-003",
        "name": "盈余分配公平性检查",
        "trigger_patterns": r"(预期分红|预计回报|projected.*return|surplus.*distribution)",
        "check_fn": None,
        "severity": "RED_LINE",
        "description": "提及预期回报时不可暗示股东优先于保单持有人",
        "regulatory_ref": "GL34 §2.5 — Surplus Distribution Fairness",
    },
    {
        "rule_id": "GL34-004",
        "name": "GN16利益区分对齐",
        "trigger_patterns": r"(\d{1,3}(?:\.\d+)?%\s*(?:利率|rate|收益|return)|演示利率)",
        "check_fn": None,
        "severity": "RED_LINE",
        "description": "数字收益表述必须明确区分保证vs非保证利益",
        "regulatory_ref": "GN16(2026.3.31) + GL34 §2.4",
    },
    {
        "rule_id": "GL34-005",
        "name": "理赔率准确性检查",
        "trigger_patterns": r"(理赔率|claim.*ratio|fulfillment.*ratio)",
        "check_fn": None,
        "severity": "YELLOW_LINE",
        "description": "必须标注数据来源和日期范围，GN16要求30年历史数据",
        "regulatory_ref": "GN16 §3.2 + 保监局理赔率通报机制(2026)",
    },
    {
        "rule_id": "GL34-006",
        "name": "演示利率上限合规检查",
        "trigger_patterns": r"(演示利率|illustration.*rate|\d+\.\d+%)",
        "severity": "RED_LINE",
        "description": "演示利率不可超过监管上限(HKD 6%, 非HKD 6.5%)，注意2026年修订至~5%/5.5%",
        "regulatory_ref": "GL34 §3.1 + GN16 demonstration rate cap",
    },
]

# 演示利率上限配置（可通过环境变量覆盖）
_ILLUSTRATION_HKD_RATE = float(os.environ.get("GL34_ILLUSTRATION_HKD_RATE", "5"))
_ILLUSTRATION_NONHKD_RATE = float(os.environ.get("GL34_ILLUSTRATION_NONHKD_RATE", "5.5"))

# GL34-002: 缺少基金隔离声明的关键词（当出现回报词但未提分离时触发）
_ABSENT_ISOLATION_WORDS = ["股东", "separate.*fund", "独立.*管理", "保单持有人"]

# GL34-003: 暗示股东优先的表达
SHAREHOLDER_PRIORITY_PATTERNS = [
    r"(股东.*[收益|分成|分配|优先])",
    r"[优先].*股东",
]

# GL34-004: 必须包含的利益区分标记
GUARANTEED_MARKERS = ["保证利益", "guaranteed benefit", "保证现金价值", "guaranteed cash value"]
NON_GUARANTEED_MARKERS = [
    "非保证利益", "non-guaranteed benefit", "演示利益", "illustration benefit",
    "非保证分红", "non-guaranteed dividend"
]

# GL34-005: 理赔率必须标注的日期/来源词
DATE_RANGE_PATTERNS = [
    r"\d{4}[年/-]\d{1,2}",
    r"[过去|近期|最新|截至]",
    r"[数据|统计|来源|根据]",
]

# ========== Rewrite Suggestions ==========

REWRITE_DB_GL34 = {
    "GL34-001": {
        "bad_keywords": [],  # PBC is about presence/absence, not specific text
        "good_phrases": ["本产品的分红运作受独立管治委员会(PBC)监管", "分红基金由独立PBC监督运作"],
    },
    "GL34-002": {
        "bad_keywords": [],
        "good_phrases": ["保单基金与股东资产完全分离管理", "分红资金独立于保险公司资产负债表"],
    },
    "GL34-003": {
        "bad_keywords": ["股东优先", "股东收益", "shareholder priority"],
        "good_phrases": ["按公平原则在保单持有人与股东间分配", "盈余分配遵循公平对待政策"],
    },
    "GL34-004": {
        "bad_keywords": [],
        "good_phrases": ["总利益=保证利益(现金价值)+非保证利益(分红)"],
    },
    "GL34-005": {
        "bad_keywords": [],
        "good_phrases": ["理赔率数据来源于保监局公布的最近年度统计", "基于过去30年历史数据计算"],
    },
    "GL34-006": {
        "bad_keywords": [r"8\.\d+%", r"7\.\d+%", "演示利率超过5%"],
        "good_phrases": [f"演示利率不超过{_ILLUSTRATION_HKD_RATE}% (HKD)", f"非港元演示利率上限{_ILLUSTRATION_NONHKD_RATE}%"],
    },
}

# ========== Core Functions ==========

def _check_absence(text: str, required_patterns: list) -> bool:
    """检查文本是否至少匹配一个必要模式"""
    for pat in required_patterns:
        if re.search(pat, text):
            return True
    return False

def _extract_rate(text: str) -> float:
    """从文本中提取数字+百分号形式的利率，返回最高值"""
    matches = re.findall(r"(\d{1,2}\.\d+)%", text)
    if matches:
        return max(float(m) for m in matches)
    return 0.0

def handle_gl34_compliance_check(params: dict) -> Dict[str, Any]:
    """GL34合规检查主入口"""
    content = params.get("content", "")
    check_type = params.get("check_type", "all")
    policy_type = params.get("policy_type", "participating")

    if not content.strip():
        return {"result": {"status": "ERROR", "message": "content cannot be empty"}}

    # 如果只查某一项，只运行对应规则
    rule_set = GL34_RULES
    if check_type != "all":
        mapping = {
            "pbc_structure": "GL34-001",
            "fund_isolation": "GL34-002",
            "surplus_distribution": "GL34-003",
            "disclosure_quality": "GL34-004",
            "claim_ratio_accuracy": "GL34-005",
            "illustration_rate": "GL34-006",
        }
        target_id = mapping.get(check_type, "GL34-001")
        rule_set = [r for r in GL34_RULES if r["rule_id"] == target_id]

    violations = []

    for rule in rule_set:
        rid = rule["rule_id"]

        # 先检查trigger是否命中
        if not re.search(rule["trigger_patterns"], content, re.IGNORECASE):
            continue

        # GL34-001: PBC管治提及
        if rid == "GL34-001":
            has_pbc = re.search(r"[Pp][Bb][Cc]|[管治治理]委员会|Board\s*[Oo]versight", content)
            if not has_pbc:
                violations.append({
                    "rule_id": rid, "name": rule["name"],
                    "severity": rule["severity"], "trigger": "分红产品讨论但未提及PBC管治",
                    "suggestion": rule["regulatory_ref"] + " → 补充独立PBC监管表述",
                    "rewrite_suggestions": REWRITE_DB_GL34[rid]["good_phrases"],
                })

        # GL34-002: 基金隔离声明
        elif rid == "GL34-002":
            has_isolation = re.search(r"分离|独立.*管理|separate.*fund|independent.*management", content, re.IGNORECASE)
            if not has_isolation:
                violations.append({
                    "rule_id": rid, "name": rule["name"],
                    "severity": rule["severity"], "trigger": "讨论回报但未声明基金隔离",
                    "suggestion": rule["regulatory_ref"] + " → 补充资产隔离说明",
                    "rewrite_suggestions": REWRITE_DB_GL34[rid]["good_phrases"],
                })

        # GL34-003: 盈余分配公平性
        elif rid == "GL34-003":
            for pat in SHAREHOLDER_PRIORITY_PATTERNS:
                if re.search(pat, content):
                    violations.append({
                        "rule_id": rid, "name": rule["name"],
                        "severity": rule["severity"], "trigger": f"发现{rid}触发",
                        "suggestion": rule["regulatory_ref"] + " → 不可暗示股东优先",
                        "rewrite_suggestions": REWRITE_DB_GL34[rid]["good_phrases"],
                    })
                    break

        # GL34-004: GN16利益区分
        elif rid == "GL34-004":
            has_guaranteed = _check_absence(content, GUARANTEED_MARKERS)
            has_nonguaranteed = _check_absence(content, NON_GUARANTEED_MARKERS)
            # Flag only when BOTH guaranteed AND non-guaranteed markers are ABSENT
            if (not has_guaranteed or not has_nonguaranteed):
                rate = _extract_rate(content)
                if rate > 0:
                    missing = []
                    if not has_guaranteed:
                        missing.append("保证利益")
                    if not has_nonguaranteed:
                        missing.append("非保证利益")
                    violations.append({
                        "rule_id": rid, "name": rule["name"],
                        "severity": rule["severity"],
                        "trigger": f"收益数字{rate}%未标注{' + '.join(missing)}区分",
                        "suggestion": rule["regulatory_ref"] + " → 明确标注保证vs非保证利益",
                        "rewrite_suggestions": REWRITE_DB_GL34[rid]["good_phrases"],
                    })

        # GL34-005: 理赔率准确性
        elif rid == "GL34-005":
            has_date = any(re.search(p, content) for p in DATE_RANGE_PATTERNS)
            if not has_date:
                violations.append({
                    "rule_id": rid, "name": rule["name"],
                    "severity": rule["severity"], "trigger": "理赔率数据未标注来源/日期",
                    "suggestion": rule["regulatory_ref"] + " → 补充数据来源和日期范围",
                    "rewrite_suggestions": REWRITE_DB_GL34[rid]["good_phrases"],
                })

        # GL34-006: 演示利率上限
        elif rid == "GL34-006":
            rate = _extract_rate(content)
            if rate > _ILLUSTRATION_HKD_RATE:
                violations.append({
                    "rule_id": rid, "name": rule["name"],
                    "severity": rule["severity"],
                    "trigger": f"演示利率{rate}%超过上限{_ILLUSTRATION_HKD_RATE}%",
                    "suggestion": f"GL34 §3.1 + GN16 → 港元演示利率上限{_ILLUSTRATION_HKD_RATE}%",
                    "rewrite_suggestions": REWRITE_DB_GL34[rid]["good_phrases"],
                })

    # Overall status
    has_critical = any(v["severity"] == "RED_LINE" for v in violations)
    overall = "BLOCKED" if has_critical else ("FLAGGED" if violations else "PASS")

    return {
        "result": {
            "gl34_status": overall,
            "violations_found": len(violations),
            "violation_details": violations,
            "red_line_count": len([v for v in violations if v["severity"] == "RED_LINE"]),
            "yellow_line_count": len([v for v in violations if v["severity"] == "YELLOW_LINE"]),
            "rule_coverage": {"gl34_rules_checked": len(rule_set), "total_gl34_rules": 6},
            "configuration": {
                "illustration_rate_hkd": _ILLUSTRATION_HKD_RATE,
                "illustration_rate_nonhkd": _ILLUSTRATION_NONHKD_RATE,
                "effective_date": "2026-03-31",
                "section4_deadline": "2026-06-30",
            },
        }
    }
