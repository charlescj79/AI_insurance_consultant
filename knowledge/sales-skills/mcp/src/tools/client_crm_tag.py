#!/usr/bin/env python3
"""Tool 8: CRM标签同步与分级管理 (client_crm_tag) + Tool 9: 多轮对话 (multi_turn_dialogue)"""
import time, json
from datetime import datetime
from typing import Dict, Any

CRM_TAG_CATEGORIES = {
    "risk_profile": {"labels": ["健康风险型", "收入保障型", "家庭责任型", "储蓄养老型", "跨境需求型", "境外医疗型"], "weight_source": "needs_assessment"},
    "purchase_intent": {"labels": ["高意向(ready)", "中意向(concerned)", "低意向(browsing)", "冷客户(cooled)"], "weight_source": "engagement_score"},
    "compliance_flag": {"labels": ["无风险(clean)", "黄线提醒(yellow_warned)", "红线阻断(red_blocked)", "敏感标签(sensitive)"], "weight_source": "compliance_check"},
    "lifecycle_stage": {"labels": ["D0_D1", "D2_D4", "D5_D7", "D8_D14", "D15_D30"], "weight_source": "last_touch_day"},
    "communication_pref": {"labels": ["文字型(wechat)", "语音型(call)", "图文型(moments)", "不敏感(not_responsive)"], "weight_source": "interaction_history"},
}

_NEED_MAP = {"health_concern": "健康风险型", "medical_need": "医疗保障型", "income_protection": "收入保障型",
             "family_responsibility": "家庭责任型", "savings_plan": "储蓄养老型", "cross_border": "跨境需求型",
             "travel_fear": "境外医疗型"}

_DEMO_CRM_DB = {}

# In-memory session store (Tool 9)
_SESSION_STORE: Dict[str, dict] = {}

def _get_lc_stage(last_touch: int) -> str:
    if last_touch <= 1: return "D0_D1"
    if last_touch <= 4: return "D2_D4"
    if last_touch <= 7: return "D5_D7"
    if last_touch <= 14: return "D8_D14"
    return "D15_D30"

def handle_client_crm_tag(params: dict) -> Dict[str, Any]:
    """Tool 8 handler"""
    action = params.get("action", "generate")
    session_id = params.get("session_id", params.get("sid", ""))

    if action == "generate":
        grade = params.get("customer_grade", "D")
        needs = params.get("needs_detected", [])
        engagement = float(params.get("engagement_score", 0.1))
        compliance_status = params.get("compliance_status", "clean")
        last_touch = int(params.get("last_touch_day", 0))

        risk_tags = [_NEED_MAP.get(n) for n in needs if n in _NEED_MAP]
        if engagement >= 0.7: intent_tag = "高意向(ready)"
        elif engagement >= 0.4: intent_tag = "中意向(concerned)"
        elif engagement >= 0.15: intent_tag = "低意向(browsing)"
        else: intent_tag = "冷客户(cooled)"

        comp_map = {"PASS": "无风险(clean)", "FLAGGED": "黄线提醒(yellow_warned)", "BLOCKED": "红线阻断(red_blocked)"}

        tags = {
            "risk_profile": risk_tags if risk_tags else ["未分类"],
            "purchase_intent": intent_tag,
            "compliance_flag": comp_map.get(compliance_status, "无风险(clean)"),
            "lifecycle_stage": _get_lc_stage(last_touch),
            "customer_grade": grade
        }
        if session_id:
            _DEMO_CRM_DB[session_id] = tags
        return {"result": {"action": "tags_generated", "session_id": session_id, "tags": tags, "tag_categories": list(CRM_TAG_CATEGORIES.keys())}}

    elif action == "query":
        tags = _DEMO_CRM_DB.get(session_id)
        return {"result": {"session_id": session_id, "tags": tags or {}}}

    elif action == "export_all":
        return {"result": {"total_customers": len(_DEMO_CRM_DB), "customers": _DEMO_CRM_DB}}

    elif action == "categorize_tags":
        return {"result": CRM_TAG_CATEGORIES}

    return {"error": "invalid_action", "available_actions": ["generate", "query", "export_all", "categorize_tags"]}


# ===================== Tool 9: Multi-turn Dialogue =====================

def _init_session(sid: str, scenario: str = "") -> dict:
    if sid not in _SESSION_STORE:
        _SESSION_STORE[sid] = {
            "session_id": sid, "created_at": datetime.now().isoformat() + "Z",
            "turn_count": 0, "context_window": [], "max_context_turns": 80,
            "customer_grade": "D", "urgency": "cold", "needs_detected": [],
            "intent_history": [], "compliance_flags": [], "products_discussed": [],
            "sop_day": 0, "total_ctas_sent": 0, "customer_profile": {},
        }
    return _SESSION_STORE[sid]

def handle_multi_turn_dialogue(params: dict) -> Dict[str, Any]:
    """Tool 9 handler"""
    action = params.get("action", "create")
    session_id = params.get("session_id", params.get("sid", ""))

    if action == "create":
        sid = session_id or f"sess_{int(time.time())}_{hash(params.get('scenario', '')) % 10000}"
        sess = _init_session(sid, params.get("scenario", ""))
        return {"result": {"action": "session_created", "session_id": sid, "status": "active", "context_window_size": 80}}

    elif action == "add_turn":
        if not session_id:
            return {"error": "session_id_required"}
        sess = _init_session(session_id)
        turn_data = {"turn": sess["turn_count"] + 1, "role": params.get("role", "user"),
                     "content": params.get("content", ""), "extracted_needs": params.get("extracted_needs", []),
                     "grade_at_turn": params.get("grade"), "timestamp": datetime.now().isoformat() + "Z"}
        sess["turn_count"] += 1
        sess["context_window"].append(turn_data)
        if len(sess["context_window"]) > sess["max_context_turns"]:
            sess["context_window"] = sess["context_window"][-sess["max_context_turns"]:]
        new_grade = params.get("grade", sess.get("customer_grade"))
        return {"result": {"action": "turn_added", "session_id": session_id, "turn_count": sess["turn_count"],
                "context_window_size": len(sess["context_window"]), "current_grade": new_grade}}

    elif action == "get_context":
        if not session_id:
            return {"error": "session_id_required"}
        sess = _SESSION_STORE.get(session_id)
        if not sess:
            return {"error": "session_not_found"}
        return {"result": {"session_id": session_id, "turn_count": sess["turn_count"], "customer_grade": sess["customer_grade"],
                "urgency": sess["urgency"], "context_summary": [t for t in sess["context_window"][-10:]]}}

    elif action == "summarize":
        if not session_id:
            return {"error": "session_id_required"}
        sess = _SESSION_STORE.get(session_id)
        if not sess:
            return {"error": "session_not_found"}
        needs = list(set(n for t in sess["context_window"] for n in t.get("extracted_needs", [])))
        score = min(100, len(needs) * 20 + (30 if sess["customer_grade"] in ["A", "B"] else 0))
        return {"result": {"action": "summary_generated", "session_id": session_id, "total_turns": sess["turn_count"],
                "key_needs": needs[:5], "estimated_conversion_score": score,
                "next_recommended_action": "consultation_booking" if sess["customer_grade"] in ["A", "B"] and sess["turn_count"] >= 4 else "content_nurture"}}

    elif action == "list_sessions":
        return {"result": {"active_sessions": len(_SESSION_STORE), "sessions": [{"id": k, "turns": v["turn_count"], "grade": v["customer_grade"]} for k, v in _SESSION_STORE.items()]}}

    elif action == "delete":
        if session_id in _SESSION_STORE:
            del _SESSION_STORE[session_id]
            return {"result": {"action": "session_deleted", "session_id": session_id}}
        return {"error": "session_not_found"}

    return {"error": "invalid_action", "available_actions": ["create", "add_turn", "get_context", "summarize", "list_sessions", "delete"]}
