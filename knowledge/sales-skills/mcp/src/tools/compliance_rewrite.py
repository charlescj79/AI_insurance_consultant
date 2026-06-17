#!/usr/bin/env python3
"""Tool 6: 违规内容自动改写 (compliance_rewrite)"""
import re
from typing import Dict, Any, List

REWRITE_DB = {
    "RL-001": {"bad": ["最高赔付", "保额可达", "最高可保"], "good": ["依合同约定给付保险金", "可获保障金额取决于保单条款"]},
    "RL-002": {"bad": ["年化.*%", "保本保息", "稳赚", "回报率", "收益率", "保证回报"], "good": ["长期锁定确定性现金流", "按合同约定分配收益"]},
    "RL-003": {"bad": ["大陆.*不如", "内地.*差", "相比香港.*优势"], "good": ["港陆保障制度各有特点", "两地制度差异可通过专业顾问解读"]},
    "RL-004": {"bad": ["内地客户专享", "仅限大陆", "大陆专属", "全国发售"], "good": ["适合有跨境保障需求的客户", "全球身份均可适用"]},
    "RL-005": {"bad": ["最快.*天", "即时赔付", "秒赔", "当天到账"], "good": ["依合同约定期限办理理赔", "理赔时效依保单条款执行"]},
    "RL-007": {"bad": ["内地可线上办理", "跨境投保最简单"], "good": ["须于香港境内完成投保流程", "具体流程由持牌中介人指导"]},
    "RL-008": {"bad": ["资金自由进出", "无需资金来源声明"], "good": ["资金来源合规需备妥证明文件", "依HKMA反洗钱要求需提供来源证明"]},
    "RL-009": {"bad": ["赶在新规前上车", "最后一波.*佣金"], "good": ["建议根据自身需求做合理规划", "不受时间压力影响做出决策"]},
}

def handle_compliance_rewrite(params: dict) -> Dict[str, Any]:
    """Tool 6 handler"""
    text = params.get("text", "")
    target_rules = params.get("target_rules", [])
    if not text:
        return {"error": "text_required"}

    # Import RED_LINE_RULES + YELLOW_LINE_RULES from compliance_check module
    import sys, os
    _cp = os.path.dirname(os.path.abspath(__file__))
    _parent = os.path.dirname(_cp)
    sys.path.insert(0, _parent)
    from tools.compliance_check import scan_rules, RED_LINE_RULES, YELLOW_LINE_RULES

    violations = scan_rules(text, RED_LINE_RULES + YELLOW_LINE_RULES)
    if not violations:
        return {"result": {"status": "no_violations", "original_text": text, "rewrite_applied": False, "changes": []}}

    filtered = [v for v in violations if not target_rules or v["rule_id"] in target_rules]
    rewritten = text
    changes = []
    for v in filtered:
        rule_id = v["rule_id"]
        info = REWRITE_DB.get(rule_id)
        if info:
            for bad_pattern in info["bad"]:
                new_texts = [r for r in info["good"] if re.search(bad_pattern, rewritten, re.IGNORECASE)]
                if new_texts:
                    old_match = re.search(bad_pattern, rewritten, re.IGNORECASE)
                    if old_match:
                        replacement = new_texts[0]
                        rewritten = re.sub(bad_pattern, replacement, rewritten, count=1, flags=re.IGNORECASE)
                        changes.append({"rule_id": rule_id, "original": old_match.group(0), "rewritten": replacement, "action": "auto_rewritten"})

    # Re-validate
    remaining_v = scan_rules(rewritten, RED_LINE_RULES + YELLOW_LINE_RULES)
    has_critical = any(v["severity"] == "CRITICAL" for v in remaining_v)
    has_high = any(v["severity"] == "HIGH" for v in remaining_v)

    if not has_critical and not has_high:
        status = "fully_compliant"
    elif has_critical:
        status = "partial_rewrite_needed"
    else:
        # Only HIGH, check original had critical
        orig_crit = any(v["severity"] == "CRITICAL" for v in violations)
        status = "partial_rewrite_needed" if orig_crit else "improved"

    return {"result": {
        "status": status, "original_text": text, "rewritten_text": rewritten,
        "changes_applied": changes, "changes_count": len(changes),
        "remaining_violations": [v["rule_id"] for v in remaining_v] if remaining_v else None,
        "requires_manual_review": status == "partial_rewrite_needed",
        "rewrite_confidence": 0.95 if status == "fully_compliant" else 0.7
    }}
