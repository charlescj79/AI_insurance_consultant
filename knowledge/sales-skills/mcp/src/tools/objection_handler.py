#!/usr/bin/env python3
"""Tool 4: 异议处理话术生成 (objection_handler)"""
import json, os
from typing import Dict, Any, Optional, List

def load_objection_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(script_dir))
    db_path = os.path.join(parent_dir, "cli", "objection-scripts-db.json")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("objection_scripts", [])
    except FileNotFoundError:
        return []

def _fuzzy_match(query_cat: str, query_scene: str, scripts: list) -> Optional[dict]:
    candidates = []
    for s in scripts:
        if query_cat and s.get("category") != query_cat:
            continue
        scene_score = 0
        if query_scene:
            scenario_text = (s.get("scenario", "") + s.get("scenario_cn", "")).lower()
            q_lower = query_scene.lower()
            if q_lower in scenario_text:
                scene_score += 10
            else:
                words = q_lower.split() if ' ' in q_lower else [q_lower]
                for word in words:
                    if len(word) >= 2 and word in scenario_text:
                        scene_score += 3
        else:
            scene_score = 1
        candidates.append((scene_score, s))
    if candidates:
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]
    return None

def handle_objection_handler(params: dict) -> Dict[str, Any]:
    """Tool 4 handler"""
    scripts = load_objection_db()
    if not scripts:
        return {"error": "objection_db_not_found"}

    action_list = params.get("list_all", False)
    if action_list:
        by_cat = {}
        for s in scripts:
            cat = s["category"]
            by_cat.setdefault(cat, []).append({"scenario": s["scenario"], "scenario_cn": s["scenario_cn"]})
        return {"result": {"action": "list_all_scenarios", "total_scenarios": len(scripts), "categories": by_cat, "tier_options": ["light", "medium", "heavy"]}}

    category = params.get("category")
    scenario = params.get("scenario", "")
    tier = params.get("tier", "medium")

    matched = _fuzzy_match(category, scenario, scripts)
    if not matched:
        return {"error": "no_matching_scenario", "suggestion": "请提供准确的异议类型或场景关键词", "available_categories": list({s["category"] for s in scripts})}

    tier_data = None
    for t in matched.get("tier_levels", []):
        if t["level"] == tier:
            tier_data = t
            break
    if not tier_data and matched.get("tier_levels"):
        tier_data = matched["tier_levels"][0]

    return {"result": {
        "category": matched["category"],
        "scenario_en": matched.get("scenario", ""),
        "scenario_cn": matched.get("scenario_cn", ""),
        "tier_requested": tier,
        "tone": tier_data.get("tone", "professional") if tier_data else "unknown",
        "script": tier_data.get("script", "") if tier_data else "",
        "full_tier_options": [{"level": t["level"], "tone": t["tone"], "script": t["script"]} for t in matched.get("tier_levels", [])]
    }}
