#!/usr/bin/env python3
"""Tool 10: 合规趋势分析 (compliance_trend_analysis)"""
import json, os
from typing import Dict, Any, List
from datetime import datetime

_HISTORY_FILE = None

def _get_history_path():
    global _HISTORY_FILE
    if _HISTORY_FILE:
        return _HISTORY_FILE
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(os.path.dirname(script_dir))
    _HISTORY_FILE = os.path.join(parent, "compliance_history.json")
    return _HISTORY_FILE

def _load_history() -> List[dict]:
    path = _get_history_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _save_history(history: List[dict]):
    path = _get_history_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def handle_compliance_trend_analysis(params: dict) -> Dict[str, Any]:
    """Tool 10 handler"""
    action = params.get("action", "analyze")

    if action == "record":
        session_id = params.get("session_id")
        status = params.get("status", "PASS")
        violations = params.get("violations", [])
        strict_mode = params.get("strict_mode", False)
        history = _load_history()
        history.append({"session_id": session_id, "status": status, "violations": violations,
                        "strict_mode": strict_mode, "timestamp": datetime.now().isoformat() + "Z"})
        _save_history(history[-100:])  # Keep last 100
        return {"result": {"action": "recorded", "total_records": len(history)}}

    elif action == "get_rule_stats":
        history = _load_history()
        # Import rules from compliance_check
        sys_path = os.path.dirname(os.path.abspath(__file__))
        import sys; sys.path.insert(0, os.path.dirname(sys_path))
        from tools.compliance_check import RED_LINE_RULES, YELLOW_LINE_RULES

        stats = {}
        for rule in RED_LINE_RULES + YELLOW_LINE_RULES:
            rid = rule["rule_id"]
            hits = sum(1 for e in history for v in e.get("violations", []) if isinstance(v, dict) and v.get("rule_id") == rid)
            stats[rid] = {"rule_name": rule["name"], "severity": rule["severity"], "total_hits": hits}
        return {"result": {"rule_statistics": stats, "total_rules_monitored": len(RED_LINE_RULES) + len(YELLOW_LINE_RULES)}}

    elif action == "analyze":
        history = _load_history()[-50:]
        if not history:
            return {"result": {"status": "no_history", "message": "尚无合规历史数据，请先使用compliance_check记录结果"}}

        violation_counts: Dict[str, int] = {}
        blocked_count = flagged_count = 0
        for entry in history:
            status = entry.get("status", "")
            if status == "BLOCKED": blocked_count += 1
            elif status == "FLAGGED": flagged_count += 1
            for v in entry.get("violations", []):
                rid = v.get("rule_id", "unknown") if isinstance(v, dict) else "unknown"
                violation_counts[rid] = violation_counts.get(rid, 0) + 1

        top_violations = sorted(violation_counts.items(), key=lambda x: -x[1])[:5]
        total = len(history)
        vr = (blocked_count + flagged_count) / max(total, 1)
        risk = "HIGH" if vr > 0.6 else ("MEDIUM" if vr > 0.3 else "LOW")
        rec = "立即审查所有待发布内容，建立合规预审流程" if risk == "HIGH" else ("加强内容审核频次" if risk == "MEDIUM" else "维持当前合规标准")

        return {"result": {
            "status": "analysis_complete", "total_checks": total,
            "violation_rate": round(vr, 3), "blocked_count": blocked_count,
            "flagged_count": flagged_count, "risk_level": risk,
            "top_violations": [{"rule_id": r, "count": c} for r, c in top_violations],
            "compliance_trend": "improving" if blocked_count > flagged_count else "stable",
            "recommendation": rec,
            "policy_update_needed": [r for r, c in top_violations if c > 3][:2] if any(c > 3 for _, c in top_violations) else []
        }}

    return {"error": "invalid_action", "available_actions": ["analyze", "record", "get_rule_stats"]}
