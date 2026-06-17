#!/usr/bin/env python3
"""
Insurance Sales MCP Session Manager — R26 (Module A.5)
======================================================
Multi-turn conversation state tracking with persistent storage.

Features:
- Memory + disk dual-layer storage (80-turn context window, R26 expanded from 10)
- Grade evolution tracking (A/B/C/D change history)
- Intent evolution engine + priority drift detection
- Compliance memory for auto-rewrite guidance
- Full lifecycle management aligned with AGENTIC-WORKFLOW-DESIGN.md v2.1

Usage:
    python3 session_manager.py create <sid>
    python3 session_manager.py add-turn <sid> --message "text"
    python3 session_manager.py list [--limit N]
    python3 session_manager.py export <sid>
    python3 session_manager.py summarize <sid>
"""

import json, os, sys, re
from datetime import datetime
from typing import Any, Dict, List, Optional


class DialogueSession:
    """Multi-turn conversation state machine (aligned with v2.1 spec)."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turn_count = 0
        self.created_at = datetime.now().isoformat() + "Z"
        self.updated_at = self.created_at
        self.customer_grade_evolution: List[str] = []
        self.context_window: List[Dict[str, Any]] = []
        self.max_context_turns = 80  # R26: expanded from 10
        self.intent_history: List[Dict[str, Any]] = []
        self.needs_evolved: List[Dict[str, Any]] = []
        self.priority_drift_detected = False
        self.last_priority_drift_turn = None
        self.compliance_flags: List[Dict[str, Any]] = []
        self.sop_day = 0
        self.total_ctas_sent = 0
        self.products_discussed: List[str] = []
        self.customer_profile: Dict[str, Any] = {}

    def add_turn(self, turn_data: Dict[str, Any]) -> None:
        """Add a conversation turn to context window."""
        self.turn_count += 1
        grade_from_turn = turn_data.get("grade")
        if grade_from_turn:
            self.set_grade(grade_from_turn)

        entry = {
            "turn": self.turn_count,
            "role": turn_data.get("role", "user"),
            "content": turn_data.get("content", ""),
            "extracted_needs": turn_data.get("extracted_needs", []),
            "grade_at_turn": grade_from_turn or self.get_grade(),
            "compliance_checked": turn_data.get("compliance_checked", False),
            "timestamp": datetime.now().isoformat() + "Z"
        }
        self.context_window.append(entry)

        # Sliding window (max 80 turns)
        if len(self.context_window) > self.max_context_turns:
            self.context_window = self.context_window[-self.max_context_turns:]

        profile = turn_data.get("customer_profile", {})
        if profile:
            self.customer_profile.update(profile)

        product = turn_data.get("product_discussed")
        if product and product not in self.products_discussed:
            self.products_discussed.append(product)

        compliance_result = turn_data.get("compliance_result")
        if compliance_result:
            status = compliance_result.get("compliance_status", "")
            if status in ("BLOCKED", "FLAGGED"):
                self.compliance_flags.append({
                    "turn": self.turn_count,
                    "status": status,
                    "violations": compliance_result.get("violation_details", [])[:3]
                })

    def detect_intent_evolution(self) -> Dict[str, Any]:
        if not self.needs_evolved:
            return {"current_intent": "unclear", "confidence": 0.3}
        intent_map = {}
        for need in self.needs_evolved[-self.max_context_turns:]:
            for intent, types in {
                "health": ["health_concern", "medical_need"],
                "family": ["income_protection", "family_responsibility"],
                "savings": ["savings_plan"],
                "travel": ["travel_fear"],
                "property": ["property_risk"],
                "cross_border": ["cross_border"],
                "objection": ["price", "trust", "delay", "compare"],
            }.items():
                if need.get("need_type") in types:
                    intent_map[intent] = intent_map.get(intent, 0) + need.get("confidence", 0)
        if not intent_map:
            return {"current_intent": "unclear", "confidence": 0.3}
        best_intent = max(intent_map, key=intent_map.get)
        confidence = min(0.95, intent_map[best_intent] / len(self.needs_evolved))
        self.intent_history.append({"turn": self.turn_count, "intent": best_intent, "confidence": round(confidence, 2)})
        return {"current_intent": best_intent, "confidence": round(confidence, 2)}

    def detect_priority_drift(self, threshold=0.15) -> Dict[str, Any]:
        if len(self.needs_evolved) < 2:
            return {"drift_detected": False}
        first_top = self.needs_evolved[0]
        latest_top = max(self.needs_evolved, key=lambda n: n.get("confidence", 0))
        confidence_diff = abs(latest_top.get("confidence", 0) - first_top.get("confidence", 0))
        need_type_changed = first_top.get("need_type") != latest_top.get("need_type")
        if need_type_changed and confidence_diff > threshold:
            self.priority_drift_detected = True
            self.last_priority_drift_turn = self.turn_count
            return {
                "drift_detected": True, "drift_type": "primary_need_switch",
                "from_need": first_top.get("need_type"), "to_need": latest_top.get("need_type"),
                "confidence_change": round(confidence_diff, 2), "detected_at_turn": self.turn_count
            }
        return {"drift_detected": False}

    def get_grade(self) -> str:
        return self.customer_grade_evolution[-1] if self.customer_grade_evolution else "D"

    def set_grade(self, new_grade: str) -> None:
        if not self.customer_grade_evolution or self.customer_grade_evolution[-1] != new_grade:
            self.customer_grade_evolution.append(new_grade)
            self.updated_at = datetime.now().isoformat() + "Z"

    def get_compliance_memory(self, window=5) -> Dict[str, Any]:
        recent = self.compliance_flags[-window:] if len(self.compliance_flags) > window else self.compliance_flags
        bans = set()
        for flag in recent:
            for v in flag.get("violations", []):
                bans.add(v.get("rule_id"))
        return {
            "prohibited_rules": list(bans),
            "last_violation_at_turn": self.compliance_flags[-1]["turn"] if self.compliance_flags else None,
            "auto_rewrites_needed": [v.get("suggestion", "") for f in recent for v in f.get("violations", [])],
            "total_violations": len(self.compliance_flags)
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id, "turn_count": self.turn_count,
            "context_window_size": len(self.context_window), "customer_grade": self.get_grade(),
            "grade_evolution": self.customer_grade_evolution, "intent_history": self.intent_history[-5:],
            "needs_evolved": self.needs_evolved,  # R27 fix: serialize actual list not count
            "priority_drift_detected": self.priority_drift_detected,
            "compliance_flags": self.compliance_flags,
            "sop_day": self.sop_day,
            "cta_count": self.total_ctas_sent, "products_discussed": self.products_discussed,
            "customer_profile": self.customer_profile, "created_at": self.created_at, "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class SessionManager:
    """Session manager with memory+disk dual-layer storage."""

    def __init__(self, sessions_dir: Optional[str] = None):
        self.sessions_dir = sessions_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cli", "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        self._cache: Dict[str, DialogueSession] = {}

    def _session_path(self, session_id: str) -> str:
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
        return os.path.join(self.sessions_dir, f"{safe_id}.json")

    def create_session(self, session_id: str) -> DialogueSession:
        if session_id in self._cache:
            return self._cache[session_id]
        session = DialogueSession(session_id)
        self._cache[session_id] = session
        self._persist(session)
        return session

    def get_session(self, session_id: str) -> Optional[DialogueSession]:
        if session_id in self._cache:
            return self._cache[session_id]
        path = self._session_path(session_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        session = DialogueSession(session_id)
        session.turn_count = data.get("turn_count", 0)
        session.context_window = data.get("context_window", [])
        session.customer_grade_evolution = data.get("grade_evolution", ["D"]) if data.get("grade_evolution") else ["D"]
        session.intent_history = data.get("intent_history", [])
        # R27 fix: load needs_evolved list and compliance_flags properly
        session.needs_evolved = data.get("needs_evolved", [])
        session.compliance_flags = data.get("compliance_flags", [])
        session.priority_drift_detected = data.get("priority_drift_detected", False)
        session.sop_day = data.get("sop_day", 0)
        session.total_ctas_sent = data.get("cta_count", 0)
        session.products_discussed = data.get("products_discussed", [])
        session.customer_profile = data.get("customer_profile", {})
        self._cache[session_id] = session
        return session

    def add_turn_to_session(self, session_id: str, turn_data: Dict[str, Any]) -> DialogueSession:
        session = self.get_session(session_id) or self.create_session(session_id)
        session.add_turn(turn_data)
        extracted_needs = turn_data.get("extracted_needs", [])
        for need in extracted_needs:
            session.needs_evolved.append(need)
        session.detect_intent_evolution()
        session.detect_priority_drift()
        # Persist after every add-turn (critical for cross-invocation state)
        self._persist(session)
        return session

    def _persist(self, session: DialogueSession) -> None:
        with open(self._session_path(session.session_id), "w", encoding="utf-8") as f:
            json.dump(json.loads(session.to_json()), f, indent=2, ensure_ascii=False)

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        files = sorted([f for f in os.listdir(self.sessions_dir) if f.endswith(".json")],
                      key=lambda x: os.path.getmtime(os.path.join(self.sessions_dir, x)), reverse=True)
        sessions = []
        for fname in files[:limit]:
            try:
                with open(os.path.join(self.sessions_dir, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append({
                    "session_id": data.get("session_id", fname.replace(".json","")),
                    "turn_count": data.get("turn_count", 0),
                    "customer_grade": data.get("customer_grade", "D"),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                })
            except Exception:
                pass
        return sessions

    def export_session(self, session_id: str) -> Optional[str]:
        path = self._session_path(session_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def delete_session(self, session_id: str) -> bool:
        path = self._session_path(session_id)
        if os.path.exists(path):
            os.remove(path)
            self._cache.pop(session_id, None)
            return True
        return False

    def summarize_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None
        intent_result = session.detect_intent_evolution()
        drift_result = session.detect_priority_drift()
        comp_memory = session.get_compliance_memory()
        current_needs = [n["need_type"] for n in session.needs_evolved[-3:]] if session.needs_evolved else []
        return {
            "session_id": session.session_id,
            "summary_text": f"Session {session.session_id}: {session.turn_count} turns, grade {session.get_grade()}, intent {intent_result['current_intent']}",
            "turn_count": session.turn_count,
            "current_grade": session.get_grade(),
            "grade_history": session.customer_grade_evolution,
            "primary_intent": intent_result["current_intent"],
            "intent_confidence": intent_result["confidence"],
            "priority_drift": drift_result,
            "compliance_violations": comp_memory["total_violations"],
            "needs_summary": current_needs,
            "products_discussed": session.products_discussed,
            "sop_day": session.sop_day,
            "cta_count": session.total_ctas_sent,
        }


def run_cli(args: list) -> None:
    manager = SessionManager()
    if not args or args[0] in ("help", "--help"):
        print("Session Manager CLI:")
        for c in ["create <sid>", "add-turn <sid> --message text", "list [--limit N]", "export <sid>", "summarize <sid>", "delete <sid>"]:
            print(f"  {c}")
        return

    cmd = args[0]
    if cmd == "create":
        sid = args[1] if len(args) > 1 else f"test-{int(datetime.now().timestamp())}"
        s = manager.create_session(sid)
        print(f"Created: {sid} — {s.to_json()}")

    elif cmd == "add-turn":
        sid = args[1]
        msg_text = None
        i = 2
        while i < len(args):
            if args[i] == "--message" and i+1 < len(args):
                msg_text = args[i+1]
                i += 2
            else:
                i += 1
        if not msg_text:
            print("Need --message text"); return

        # Use needs_assessment + compliance_check from server
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from server import handle_needs_assessment, handle_compliance_check

        assessment = handle_needs_assessment({"message": msg_text})
        compliance = handle_compliance_check({"text": msg_text})
        grade = assessment.get("result", {}).get("customer_grade", "D")
        needs = [n for n in assessment.get("result", {}).get("detected_needs", [])]

        turn_data = {"role":"user","content":msg_text,"extracted_needs":needs,"grade":grade,"compliance_result":compliance.get("result",{})}
        s = manager.add_turn_to_session(sid, turn_data)
        intent = s.detect_intent_evolution()
        print(f"Turn #{s.turn_count}: grade={s.get_grade()} intent={intent['current_intent']}")

    elif cmd == "list":
        limit = int(args[1]) if len(args) > 1 and args[1].startswith("--limit") else 50
        sessions = manager.list_sessions(limit)
        for s in sessions:
            print(f"  {s['session_id']}: grade={s['customer_grade']} turns={s['turn_count']}")

    elif cmd == "export":
        data = manager.export_session(args[1])
        if data:
            print(data)
        else:
            print(f"Not found: {args[1]}")

    elif cmd == "summarize":
        summary = manager.summarize_session(args[1])
        if summary:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print(f"Not found: {args[1]}")

    elif cmd == "delete":
        ok = manager.delete_session(args[1])
        print(f"{'Deleted' if ok else 'Not found'}: {args[1]}")


if __name__ == "__main__":
    run_cli(sys.argv[1:])
