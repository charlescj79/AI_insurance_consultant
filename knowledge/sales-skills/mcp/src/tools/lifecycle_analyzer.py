#!/usr/bin/env python3
"""Tool 7: 客户生命周期分析 (lifecycle_analyzer)"""
from typing import Dict, Any

LIFECYCLE_STAGES = {
    "D0_D1": {"name": "认知阶段", "duration": "0-2天", "goal": "建立信任+品牌认知", "content_type": ["科普内容", "行业解读", "政策解读"], "compliance_level": "LOW", "kpi": ["阅读率>60%", "收藏率>5%"]},
    "D2_D4": {"name": "信任阶段", "duration": "3-5天", "goal": "需求挖掘+专业度展示", "content_type": ["案例分享(脱敏)", "保险制度解析", "QA互动"], "compliance_level": "LOW-MED", "kpi": ["互动率>10%", "私信转化率>3%"]},
    "D5_D7": {"name": "方案阶段", "duration": "6-8天", "goal": "方案框架展示+初步匹配", "content_type": ["保障框架对比(无产品名)", "GN16解读", "需求测评工具"], "compliance_level": "MED", "kpi": ["CTA点击率>8%", "预约咨询>2%"]},
    "D8_D14": {"name": "决策阶段", "duration": "9-15天", "goal": "深度沟通+异议处理", "content_type": ["1v1需求梳理", "方案对比框架", "客户见证(脱敏)"], "compliance_level": "MED-HIGH", "kpi": ["预约率>15%", "咨询转化率>30%"]},
    "D15_D30": {"name": "转化/维护阶段", "duration": "16-30天", "goal": "促成+关系维护", "content_type": ["保单检视", "理赔案例(脱敏)", "周年回访"], "compliance_level": "HIGH", "kpi": ["转化率>20%", "转介绍率>5%"]}
}

RECOMMENDATION_MATRIX = {
    ("D0_D1", "A"): {"priority": "high", "next_action": "rapid_transition_D2_D4"},
    ("D0_D1", "B"): {"priority": "medium", "next_action": "content_nurture"},
    ("D2_D4", "A"): {"priority": "high", "next_action": "needs_discovery_tool"},
    ("D5_D7", "A"): {"priority": "urgent", "next_action": "consultation_booking"},
    ("D8_D14", "A"): {"priority": "critical", "next_action": "proposal_preparation"},
}

def handle_lifecycle_analyzer(params: dict) -> Dict[str, Any]:
    """Tool 7 handler"""
    action = params.get("action", "analyze")

    if action == "analyze":
        last_touch_day = int(params.get("last_touch_day", 0))
        customer_grade = params.get("customer_grade", "D")
        engagement_score = float(params.get("engagement_score", 0.3))
        if last_touch_day <= 1: stage = "D0_D1"
        elif last_touch_day <= 4: stage = "D2_D4"
        elif last_touch_day <= 7: stage = "D5_D7"
        elif last_touch_day <= 14: stage = "D8_D14"
        else: stage = "D15_D30"

        if engagement_score < 0.3: content_strategy = "content_nurture_heavy"
        elif engagement_score < 0.6: content_strategy = "content_nurture_light"
        else: content_strategy = "cta_push"

        rec = RECOMMENDATION_MATRIX.get((stage, customer_grade), {"priority": "normal", "next_action": "standard_nurture"})
        est_timeline = 7 + max(0, (last_touch_day - 5))

        return {"result": {
            "current_stage": stage, "stage_info": LIFECYCLE_STAGES[stage],
            "engagement_score": engagement_score, "content_strategy": content_strategy,
            "grade_lifecycle_rec": rec,
            "recommended_content_types": LIFECYCLE_STAGES[stage]["content_type"],
            "compliance_level": LIFECYCLE_STAGES[stage]["compliance_level"],
            "estimated_conversion_timeline_days": est_timeline,
            "optimization_suggestions": [
                f"当前处于{LIFECYCLE_STAGES[stage]['name']}阶段，建议重点提升互动质量",
                f"Grade {customer_grade}客户在{stage}阶段的平均转化周期为7-14天",
                f"推荐内容方向：{', '.join(LIFECYCLE_STAGES[stage]['content_type'])}",
            ]
        }}

    elif action == "get_stages":
        return {"result": {"lifecycle_stages": LIFECYCLE_STAGES, "total_stages": len(LIFECYCLE_STAGES)}}

    elif action == "optimize":
        grade = params.get("customer_grade", "C")
        stage = params.get("current_stage", "D2_D4")
        days_active = int(params.get("days_active", 3))
        touchpoint_count = int(params.get("touchpoint_count", 2))
        conversion_probability = float(params.get("conversion_probability", 0.15))

        suggestions = []
        if days_active < 7 and grade in ['A', 'B']:
            suggestions.append({"priority": "high", "action": "accelerate_to_D5"})
        if touchpoint_count < 3:
            suggestions.append({"priority": "medium", "action": "increase_touchpoints"})
        if conversion_probability > 0.3 and stage not in ["D8_D14", "D15_D30"]:
            suggestions.append({"priority": "critical", "action": "immediate_cta"})

        return {"result": {
            "optimization_pipeline": True,
            "current_state": {"grade": grade, "stage": stage, "days_active": days_active, "touchpoints": touchpoint_count},
            "recommendations": suggestions or [{"priority": "normal", "action": "continue_standard_nurture"}],
            "estimated_roi_days": 14 if grade == "A" else (21 if grade == "B" else 30)
        }}

    return {"error": "invalid_action", "available_actions": ["analyze", "get_stages", "optimize"]}
