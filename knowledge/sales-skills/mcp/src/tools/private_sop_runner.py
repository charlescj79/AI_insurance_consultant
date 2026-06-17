#!/usr/bin/env python3
"""Tool 5: 私域SOP执行器 (private_sop_runner)"""
from typing import Dict, Any

DAY_SEQUENCES = {
    "Day-0": {"timing": "0-2h内", "action": "welcome_message", "channels": ["wechat"], "compliance_level": "low_risk",
              "scripts": {"standard": "您好！感谢添加。我是XX保险经纪顾问，专注于香港保险制度解读与家庭保障规划。", "casual": "哈喽！终于加上了😊 我平时主要做香港保险的科普分享"},
              "rules": ["首条消息不推产品", "自我介绍需含'保险经纪顾问'身份标识"]},
    "Day-1": {"timing": "24h触发", "action": "content_nurture", "channels": ["wechat", "moments"], "compliance_level": "low_risk",
              "scripts": {"educate_gn16": "最近很多客户问香港保险新规GN16，我整理了一份解读摘要。纯科普，不涉及任何产品推荐。", "family_risk": "昨天有个客户问我'房贷+孩子=风险敞口多大'，做个简单测评或许对您有帮助"},
              "rules": ["内容必须标注'科普/教育目的'", "不得暗示购买紧迫感"]},
    "Day-3": {"timing": "72h触发", "action": "needs_discovery", "channels": ["wechat"], "compliance_level": "medium_risk",
              "scripts": {"standard": "上次分享的资料还看得明白吗？如果您有具体的保障需求，我可以帮您做个初步梳理，不涉及任何产品推荐。"},
              "rules": ["使用开放式问题引导", "不得预设客户有购买意向", "可提及'初步梳理'但必须声明非销售"]},
    "Day-5": {"timing": "120h触发", "action": "solution_education", "channels": ["wechat", "call"], "compliance_level": "medium_risk",
              "scripts": {"standard": "根据您的情况，市面上比较适合的保障框架大概有三种类型。我先帮您列一个对比框架（不涉及具体公司/产品）"},
              "rules": ["仅对B级以上客户执行", "用'框架类型'而非产品名", "必须同步展示保证利益与非保证利益的区分原则(GN16)"]},
    "Day-7": {"timing": "168h触发", "action": "cta_or_reactivate", "channels": ["wechat", "call"], "compliance_level": "high_risk",
              "scripts": {"standard_cta": "如果您觉得初步梳理有帮助，可以预约一次15分钟的电话沟通。纯需求了解，没有任何推销压力。", "reactivation_cold": "最近香港保险市场有不少新动态，想跟您分享一下是否有参考价值？"},
              "rules": ["最多触发3次CTA，之后停止主动触达", "不得制造'限时优惠'等虚假紧迫感"]},
}

CHANNEL_PRIORITY = {"wechat": {"priority": 1, "open_rate": "~85%", "compliance_risk": "low"},
    "moments": {"priority": 2, "open_rate": "~60%", "compliance_risk": "low"},
    "call": {"priority": 3, "open_rate": "~40%", "compliance_risk": "medium"},
    "email": {"priority": 4, "open_rate": "~25%", "compliance_risk": "high"}}

def handle_private_sop_runner(params: dict) -> Dict[str, Any]:
    """Tool 5 handler"""
    action = params.get("action")

    if action == "day-sequence":
        day_num = min(int(params.get("day", 3)), 7)
        key = f"Day-{day_num}"
        grade = params.get("grade", "B")
        channel = params.get("channel", "wechat")
        seq = DAY_SEQUENCES.get(key)
        if not seq:
            return {"error": "invalid_day", "available_days": list(DAY_SEQUENCES.keys())}
        if channel not in seq["channels"]:
            return {"error": "channel_not_available_for_day", "requested_channel": channel, "available_channels": seq["channels"]}
        return {"result": {"day": key, "timing": seq["timing"], "action": seq["action"], "channel": channel,
                "compliance_level": seq["compliance_level"], "recommended_scripts": seq["scripts"],
                "rules": seq["rules"], "grade_hint": f"Grade {grade}客户适用" if grade in ['A','B'] else "纯科普引导"}}

    elif action == "customer-journey":
        grade = params.get("grade", "A")
        journey = [{"day": f"D{d}", "action": ["welcome_add","content_nurture","needs_discovery","solution_or_cta","final_followup"][min(d//2, 4)],
                    "compliance_level": DAY_SEQUENCES.get(f"Day-{min(d,7)}",{}).get("compliance_level")} for d in range(8)]
        result = {"simulation": "7-day_journey", "customer_grade": grade, "total_touchpoints": 8, "journey": journey,
                  "compliance_warnings": ["D0-D1: 不得提及具体产品/收益", "D3: 必须声明'非销售'", "D5+: B级以上才可用方案框架话术", "D7: CTA最多3次，之后静默"]}
        if params.get("scenario"):
            result["scenario"] = params["scenario"]
        return {"result": result}

    elif action == "get-schedule":
        sid = params.get("sid")
        if not sid:
            return {"error": "session_id_required"}
        schedule = [{"day": key, "action": DAY_SEQUENCES.get(key,{}).get("action","final_followup"),
                     "compliance_level": DAY_SEQUENCES.get(key,{}).get("compliance_level","high_risk")} for key in DAY_SEQUENCES]
        return {"result": {"session_id": sid, "schedule": schedule, "channel_priority_matrix": CHANNEL_PRIORITY, "next_action_required": schedule[0]}}

    return {"error": "invalid_action", "available_actions": ["day-sequence", "customer-journey", "get-schedule"]}
