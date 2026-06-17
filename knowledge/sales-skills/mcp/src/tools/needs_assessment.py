#!/usr/bin/env python3
"""Tool 3: 客户需求诊断 (needs_assessment)"""
from typing import Dict, Any, List

NEED_KEYWORDS = {
    "health_concern": ["生病", "癌症", "重疾", "心脏病", "肿瘤", "确诊", "体检异常"],
    "medical_need": ["住院", "报销", "医保不够", "自费", "特需", "私立医院", "手术费"],
    "income_protection": ["收入", "工作没了", "失业", "房贷", "养家", "家人生活", "生活费"],
    "family_responsibility": ["家人", "孩子教育", "父母养老", "留爱不留债", "家庭支柱"],
    "travel_fear": ["旅游", "出差", "海外", "境外医疗", "救援", "国际就医"],
    "savings_plan": ["储蓄", "理财", "养老", "退休", "教育金", "资产配置", "资金安全"],
    "property_risk": ["火灾", "漏水", "盗窃", "家财", "物业损坏", "财产"],
    "cross_border": ["内地", "跨境", "大湾区", "海归", "外籍", "海外身份"],
    "elderly_care": ["老年", "高龄", "年纪大", "买不了保险", "既往症"],
}

def handle_needs_assessment(params: dict) -> Dict[str, Any]:
    """Tool 3 handler: needs_assessment"""
    message = params.get("message", "")
    context_history = params.get("context_history", [])
    
    signals = {}
    lower_msg = message.lower()
    for hist in context_history:
        lower_msg += " " + hist.lower()

    for need_type, keywords in NEED_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in lower_msg]
        if matched:
            confidence = min(0.9, 0.5 + 0.2 * len(matched))
            signals[need_type] = {"need_type": need_type, "confidence": round(confidence, 2), "keywords_matched": matched}

    sorted_signals = sorted(signals.values(), key=lambda x: x["confidence"], reverse=True)[:3]

    # Hidden signal detection
    hidden_health = ["结节", "囊肿", "血压高", "血糖高", "脂肪肝", "尿酸", "息肉", "炎症"]
    for kw in hidden_health:
        if kw.lower() in lower_msg and not signals.get("health_concern"):
            signals["health_concern"] = {"need_type": "health_concern", "confidence": 0.5, "keywords_matched": [kw]}
            sorted_signals = sorted(signals.values(), key=lambda x: x["confidence"], reverse=True)[:3]

    need_types = {s["need_type"] for s in sorted_signals}
    
    health_related = bool(need_types & {"health_concern", "medical_need"})
    income_family = bool(need_types & {"income_protection", "family_responsibility"})
    cross_border_flag = bool(need_types & {"cross_border"}) or any(kw in lower_msg for kw in ["内地","跨境","大湾区","海归"])
    
    grade = "D"
    if health_related and income_family:
        grade = "A"
    elif (health_related and len(sorted_signals) >= 2) or cross_border_flag:
        grade = "A"
    elif income_family or health_related:
        grade = "B"
    elif "travel_fear" in need_types or "savings_plan" in need_types:
        grade = "C"

    urgent_kw = ["马上", "着急", "最近", "刚发现", "担心", "焦虑", "怎么办"]
    warm_kw = ["考虑", "想咨询", "打算", "了解", "计划"]
    urgency = "cold"
    if any(kw in lower_msg for kw in urgent_kw):
        urgency = "urgent"
    elif any(kw in lower_msg for kw in warm_kw):
        urgency = "warm"

    need_names = {
        "health_concern": "健康风险", "medical_need": "医疗保障",
        "income_protection": "收入保护", "family_responsibility": "家庭责任",
        "travel_fear": "跨境/境外医疗", "savings_plan": "储蓄养老规划",
        "property_risk": "财产保障", "cross_border": "跨境保险需求",
        "elderly_care": "老年保障"
    }

    product_map = {
        "health_concern": ("重疾险", "确诊合同约定的疾病后,一次性给付保险金"),
        "medical_need": ("医疗险", "补充社保报销范围之外的高额医疗费用"),
        "income_protection": ("定期寿险", "保障期内因身故/全残给付保险金"),
        "family_responsibility": ("定期寿险+重疾险组合", "构建家庭财务安全网"),
        "travel_fear": ("全球医疗险", "覆盖全球医疗机构的医疗费用"),
        "savings_plan": ("年金险", "通过长期储蓄型产品锁定确定性"),
        "cross_border": ("全球医疗险", "跨境身份人群的保障规划"),
    }

    product_recommendation = None
    if grade in ['A', 'B'] and sorted_signals:
        primary = sorted_signals[0]["need_type"]
        core, desc = product_map.get(primary, ("待定", ""))
        product_recommendation = {"core_product": core, "action": "consultation_booking" if grade in ['A','B'] else "content_nurture"}

    return {
        "result": {
            "detected_needs": sorted_signals,
            "customer_grade": grade,
            "urgency": urgency,
            "product_recommendation": product_recommendation,
            "needs_summary": f"检测到{len(sorted_signals)}个风险信号: {', '.join(need_names.get(s['need_type'], s['need_type']) for s in sorted_signals) if sorted_signals else '无明确信号'}",
            "context_enhanced": len(context_history) > 0,
            "context_turns_considered": len(context_history),
        }
    }
