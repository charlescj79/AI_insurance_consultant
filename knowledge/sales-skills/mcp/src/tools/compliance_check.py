#!/usr/bin/env python3
"""Tool 2: 合规检测引擎 (compliance_check) — GL-44 / GN16 规则 + R46 智能分类"""
import re
from typing import Dict, Any, List

RED_LINE_RULES = [
    {"rule_id": "RL-001", "name": "产品宣传禁则", "pattern": r"(最高赔付|保额可达|最高可保)", "severity": "CRITICAL"},
    {"rule_id": "RL-002", "name": "收益承诺禁则", "pattern": r"(年化.*%|保本保息|稳赚|回报率|收益率|保证回报)", "severity": "CRITICAL"},
    {"rule_id": "RL-003", "name": "贬低同业禁则", "pattern": r"(大陆.*不如|内地.*差|相比香港.*优势|香港比大陆|相比内地.*强|对比内地.*优)", "severity": "CRITICAL"},
    {"rule_id": "RL-004", "name": "内地招揽禁则", "pattern": r"(内地客户专享|仅限大陆|大陆专属|全国发售|面向国内)", "severity": "CRITICAL"},
    {"rule_id": "RL-005", "name": "理赔速度承诺", "pattern": r"(最快.*天|即时赔付|秒赔|当天到账|闪电理赔)", "severity": "CRITICAL"},
    {"rule_id": "RL-006", "name": "具体产品名+保额组合", "pattern": r"([a-zA-Z\u4e00-\u9fa5]+保险).*(\d{3,}\s*万|百万)", "severity": "HIGH"},
    {"rule_id": "RL-007", "name": "内地推介禁则", "pattern": r"(内地客户专享|全国发售|面向国内|仅限大陆|跨境投保最简单|内地可线上办理)", "severity": "CRITICAL"},
    {"rule_id": "RL-008", "name": "资金来源虚假声明", "pattern": r"(资金自由进出|无需资金来源声明|跨境资金不受限|资金随意调拨)", "severity": "CRITICAL"},
    {"rule_id": "RL-009", "name": "佣金新规催单禁则", "pattern": r"(赶在新规前上车|最后一波.*佣金|最后一波.*优惠|限时高返佣)", "severity": "CRITICAL"},
    {"rule_id": "RL-010", "name": "跨境政策不确定性禁则", "pattern": r"(深圳.*子公司.*即将开业|跨境资金结算.*更便利|深港互通.*无跨境限制|内地医疗直连.*已实现|资金不受5万美金限制)", "severity": "CRITICAL"},
    # R46新增: 主动推荐香港保险给内地客户 = 红线（无论谁发起，推荐行为本身违规）
    {"rule_id": "RL-011", "name": "主动推荐禁则", "pattern": r"(建议.*投保|推荐.*您|强烈推荐.*险|适合.*购买|可以考虑.*香港险|帮您选.*港险|这款.*适合.*您)", "severity": "CRITICAL"},
]

YELLOW_LINE_RULES = [
    {"rule_id": "YL-001", "name": "避免绝对化用语", "pattern": r"(一定|肯定|绝对|100%.*[能够]|永远)", "severity": "MEDIUM"},
    {"rule_id": "YL-002", "name": "避免制造焦虑/紧迫感", "pattern": r"(不买就后悔|最后机会|限时优惠|错过等一年|即将截止|仅剩.*)", "severity": "MEDIUM"},
    {"rule_id": "YL-003", "name": "赴港投保流程规范缺失", "pattern": r"(线上办理|无需面签|远程投保|大陆可办)", "severity": "MEDIUM"},
    {"rule_id": "YL-005", "name": "GN16利益区分缺失", "pattern": r"(总收益包含演示利益|未区分.*非保证|仅展示.*演示|不分.*利益)", "severity": "MEDIUM"},
]

REGULATORY_REFS = {
    "RL-001": "GL-44《保险中介人准则》§5.2",
    "RL-002": "银保监〔2019〕39号文",
    "RL-003": "GL-44 §8.3",
    "RL-004": "《保险法》第8条 + 保监会跨境业务监管规定",
    "RL-005": "GL-44 §5.2",
    "RL-006": "GL-44 §4.1",
    "RL-007": "保监局跨境销售监管(2026-06-01通报)",
    "RL-008": "HKMA反洗钱要求 (2026-05)",
    "RL-009": "保监局分红保单佣金新规(2026年1月)",
    "RL-010": "保监局访客定义更新 + 深圳保险北上政策(2026)",
    "RL-011": "GL-44 §8.3 + 保监局跨境业务监管(2026)",
    "YL-001": "GL-44 §5.2 精神",
    "YL-002": "《保险营销管理办法》",
    "YL-003": "保监局赴港投保流程要求(2026-06-01通报)",
    "YL-005": "GN16(2026.3.31生效) + 指引34",
}

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

# R46新增: 查询意图关键词（用户主动询问知识/信息）
QUERY_INTENT_PATTERNS = [
    r"(什么是|怎么理解|能解释.*吗|请问.*是什么|.*什么意思|.*和.*区别|.*流程是怎样的|.*条件要求|.*需要什么资料)",
    r"(想了解|想问|求教|咨询一下|帮我查|告诉我.*知识|.*是怎么运作的)",
    r"(分红实现率怎么查|GN16规定|保监局.*指引34|香港保险.*制度|赴港投保.*流程|.*内地保险.*规定)",
]

# R46新增: 主动推荐意图关键词（触发拦截）
PUSH_INTENT_PATTERNS = [
    r"(建议购买|推荐您|为您推荐|强烈建议您|适合您买|帮您选|赶紧入手|值得投资|闭眼入)",
    r"(香港保险.*好|港险.*划算|比内地.*强|大陆.*不如|.*更值得买)",
    r"(联系我投保|加我微信咨询|私信获取方案|预约投保|点击链接购买)",
]

DISCLAIMER_TEXT = "本回答仅供参考，不构成专业保险意见。如有需要，请咨询持牌保险中介人。"


def _classify_intent(text: str) -> str:
    """R46: 分类意图 — query / push / neutral"""
    for pat in PUSH_INTENT_PATTERNS:
        if re.search(pat, text):
            return "push"
    for pat in QUERY_INTENT_PATTERNS:
        if re.search(pat, text):
            return "query"
    return "neutral"


def scan_rules(text: str, rules: list) -> List[dict]:
    """对一组规则扫描文本，返回违规列表"""
    violations = []
    for rule in rules:
        matches = re.findall(rule["pattern"], text, re.IGNORECASE)
        if matches:
            violations.append({
                "rule_id": rule["rule_id"],
                "name": rule["name"],
                "severity": rule["severity"],
                "matched_text": matches[0],
                "suggestion": REGULATORY_REFS.get(rule["rule_id"], ""),
                "regulatory_ref": REGULATORY_REFS.get(rule["rule_id"], ""),
            })
    return violations


def _status_from_violations(violations: list) -> str:
    has_critical = any(v["severity"] == "CRITICAL" for v in violations)
    has_high = any(v["severity"] == "HIGH" for v in violations)
    if has_critical:
        return "BLOCKED"
    if has_high:
        return "FLAGGED"
    return "PASS"


def handle_compliance_check(params: dict) -> Dict[str, Any]:
    """Tool 2 handler: compliance_check (R46 智能分类模式)

    R46策略变更：
    - RL-011(主动推荐) = 永久红线，不论意图一律BLOCKED
    - 其他违规 + push意图 = BLOCKED
    - 其他违规 + query意图 = FLAGGED（加免责声明后可回复）
    - 无违规 + query/neutral = PASS（仍加免责声明）
    """
    text = params.get("text", "")
    strict_mode = params.get("strict_mode", False)

    # R46: 意图分类
    intent = _classify_intent(text)

    violations = scan_rules(text, RED_LINE_RULES) + scan_rules(text, YELLOW_LINE_RULES)

    if strict_mode:
        hidden = [
            ("RL-012", "隐式收益暗示", r"(投资回报|资产增值|财富增值)", "MEDIUM"),
        ]
        for rid, name, pat, sev in hidden:
            if re.search(pat, text):
                violations.append({"rule_id": rid, "name": name, "severity": sev,
                                   "matched_text": "[严格模式触发]", "suggestion": "改为'财务规划工具'"})

    # R46: 智能状态判定
    has_rl011 = any(v["rule_id"] == "RL-011" for v in violations)
    critical_violations = [v for v in violations if v.get("severity") == "CRITICAL" and v["rule_id"] != "RL-011"]

    if has_rl011:
        # RL-011 主动推荐红线，永远BLOCKED
        status = "BLOCKED"
        action_taken = "push_intercepted"
    elif critical_violations:
        # 任何CRITICAL违规 = BLOCKED（不管query/push）
        if intent == "push":
            action_taken = "push_blocked_with_violations"
        else:
            action_taken = "content_blocked_critical_violation"
        status = "BLOCKED"
    elif intent == "query" or intent == "neutral":
        # 无CRITICAL，只有黄线或无违规 → PASS + disclaimer
        status = "PASS"
        action_taken = "query_pass_with_disclaimer" if intent == "query" else "pass_with_disclaimer"
    else:
        has_high = any(v["severity"] == "HIGH" for v in violations)
        if has_high:
            status = ComplianceStatus.FLAGGED.value
            action_taken = "flagged_high"
        else:
            status = ComplianceStatus.PASS.value
            action_taken = "default_pass"
            action_taken = "default_determined"

    return {
        "result": {
            "compliance_status": status,
            "intent_classification": intent,  # R46新增
            "action_taken": action_taken,       # R46新增
            "violations_found": len(violations),
            "violation_details": violations,
            "red_line_count": len([v for v in violations if v["severity"] == "CRITICAL"]),
            "yellow_line_count": len([v for v in violations if v["severity"] == "MEDIUM"]),
            "rule_coverage": {"red_lines": len(RED_LINE_RULES), "yellow_lines": len(YELLOW_LINE_RULES)},
            "disclaimer_required": status in ["PASS", "FLAGGED"],  # R46新增
            "disclaimer_text": DISCLAIMER_TEXT,                       # R46新增
        }
    }
