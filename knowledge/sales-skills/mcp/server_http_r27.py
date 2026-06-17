#!/usr/bin/env python3
"""
保险咨询销售 MCP Server — HTTP Transport Mode + Session CRUD REST API (R27升级)
=============================================================================
协议: MCP JSON-RPC over HTTP POST
端口: 18060 (可通过环境变量 SERVER_PORT 覆盖)
依赖: Python 3.7+ stdlib only (http.server + json)

用法:
  python server_http_r27.py                     # default port 18060
  SERVER_PORT=9000 python server_http_r27.py    # custom port

新增R27 Session REST API:
  POST /sessions/create     - 创建新会话
  GET  /sessions/list       - 列出所有会话
  GET  /sessions/<sid>      - 导出会话JSON
  GET  /sessions/summarize?sid=X - 会话摘要
  POST /sessions/<sid>/add-turn   - 添加对话轮次（自动需求分析+合规检测）
  POST /sessions/<sid>/summarize  - 生成会话摘要
  POST /sessions/<sid>/delete     - 删除会话
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import the core tools from server.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import (
    handle_initialize,
    handle_tools_list,
    TOOL_HANDLERS,
)

# Import SessionManager for REST API endpoints
try:
    from session_manager import SessionManager
    HAS_SESSION_MANAGER = True
except ImportError:
    _alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cli', '..')
    sys.path.insert(0, _alt_path)
    try:
        from mcp.session_manager import SessionManager
        HAS_SESSION_MANAGER = True
    except ImportError:
        HAS_SESSION_MANAGER = False

HTTP_PORT = int(os.environ.get("SERVER_PORT", "18060"))


def _get_sm():
    if HAS_SESSION_MANAGER:
        return SessionManager()
    return None


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler that accepts JSON-RPC + Session CRUD requests"""

    def log_message(self, format, *args):
        pass

    def _read_body(self) -> bytes:
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length) if content_length > 0 else b""

    def _respond(self, code: int, body: dict):
        response = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        body_bytes = response.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def _handle_single_request(self, body_bytes: bytes) -> dict:
        """Process a single JSON-RPC request and return response dict"""
        try:
            msg_dict = json.loads(body_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {"error": {"code": -32700, "message": "Parse error"}}

        method = msg_dict.get("method", "")

        if method == "initialize":
            result = handle_initialize()
            return {"jsonrpc": "2.0", "id": msg_dict.get("id"), "result": result}

        if method == "tools/list":
            result = handle_tools_list()
            return {"jsonrpc": "2.0", "id": msg_dict.get("id"), "result": result}

        if method == "tools/call":
            tool_name = msg_dict.get("params", {}).get("name", "")
            handler = TOOL_HANDLERS.get(tool_name)
            if not handler:
                return {
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                    "id": msg_dict.get("id"),
                    "jsonrpc": "2.0",
                }
            try:
                result = handler(msg_dict.get("params", {}).get("arguments", {}))
            except Exception as e:
                result = {"error": str(e)}
            return {"jsonrpc": "2.0", "id": msg_dict.get("id"), "result": result}

        return {
            "error": {"code": -32601, "message": f"Method not found: {method}"},
            "id": msg_dict.get("id"),
            "jsonrpc": "2.0",
        }

    def do_GET(self):
        parsed = urlparse(self.path)

        # Session CRUD GET endpoints (R27新增)
        if HAS_SESSION_MANAGER:
            sm = _get_sm()
            path = parsed.path.rstrip('/')

            # GET /sessions/list — list all sessions
            if path == '/sessions/list':
                limit = int(parse_qs(parsed.query).get('limit', [50])[0])
                sessions = sm.list_sessions(limit)
                self._respond(200, {"status": "ok", "total": len(sessions), "sessions": sessions})
                return

            # GET /sessions/summarize?sid=X — session summary (BEFORE generic handler!)
            if path == '/sessions/summarize':
                q = parse_qs(parsed.query)
                sid = q.get('sid', [None])[0]
                if not sid:
                    self._respond(400, {"error": "missing_sid"})
                    return
                summary = sm.summarize_session(sid)
                if summary:
                    self._respond(200, {"status": "ok", **summary})
                else:
                    self._respond(404, {"error": "session_not_found", "session_id": sid})
                return

            # GET /sessions/<sid> — export session (generic catch-all)
            if path.startswith('/sessions/'):
                parts = path.split('/sessions/')
                sid = parts[1] if len(parts) > 1 else None
                if sid and '/' not in sid and len(sid) < 30:  # sid should be short ID
                    data = sm.export_session(sid)
                    if data:
                        self._respond(200, json.loads(data))
                    else:
                        self._respond(404, {"error": "session_not_found", "session_id": sid})
                    return

        if parsed.path == "/health":
            self._respond(200, {"status": "ok", "transport": "http", "port": HTTP_PORT})
        elif parsed.path == "/mcp/manifest":
            self._respond(200, {
                "name": "insurance-sales-mcp",
                "version": "1.1.0",
                "transport": "http",
                "endpoints": [
                    {"path": "/mcp", "method": "POST"},
                    {"path": "/health", "method": "GET"},
                    {"path": "/sessions/*", "method": "POST|GET"},  # R27新增
                ],
            })
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        body_bytes = self._read_body()

        # Session CRUD POST endpoints (R27新增)
        if HAS_SESSION_MANAGER and parsed.path.startswith('/sessions'):
            sm = _get_sm()
            path = parsed.path.rstrip('/')

            # POST /sessions/create — create new session
            if path == '/sessions/create':
                try:
                    req = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
                except Exception:
                    self._respond(400, {"error": "invalid_json"})
                    return
                sid = req.get('session_id') or req.get('sid', f'session-{int(__import__("time").time())}')
                session = sm.create_session(sid)
                self._respond(201, {
                    "status": "created",
                    "session_id": session.session_id,
                    "turn_count": session.turn_count,
                    "customer_grade": session.get_grade(),
                    "max_context_turns": session.max_context_turns
                })
                return

            # POST /sessions/<sid>/add-turn — add conversation turn
            if path.startswith('/sessions/') and path.endswith('/add-turn'):
                parts = path.split('/sessions/')
                sid = parts[1].replace('/add-turn', '')
                if not body_bytes:
                    self._respond(400, {"error": "missing_request_body"})
                    return
                try:
                    req = json.loads(body_bytes.decode('utf-8'))
                except Exception:
                    self._respond(400, {"error": "invalid_json"})
                    return
                from server import handle_needs_assessment, handle_compliance_check
                msg = req.get('message') or req.get('input', '')
                if not msg:
                    self._respond(400, {"error": "missing_message"})
                    return
                # Auto-analyze with MCP tools
                assessment = handle_needs_assessment({"message": msg, "context_history": []})
                compliance = handle_compliance_check({"text": msg})
                grade = assessment.get("result", {}).get("customer_grade", "D")
                detected_needs = [n for n in assessment.get("result", {}).get("detected_needs", [])]
                turn_data = {
                    "role": "user",
                    "content": msg,
                    "extracted_needs": detected_needs,
                    "grade": grade,
                    "compliance_result": compliance.get("result", {})
                }
                session = sm.add_turn_to_session(sid, turn_data)
                intent = session.detect_intent_evolution()
                drift = session.detect_priority_drift()
                self._respond(201, {
                    "status": "turn_added",
                    "session_id": sid,
                    "turn_count": session.turn_count,
                    "grade": session.get_grade(),
                    "intent": intent,
                    "priority_drift": drift
                })
                return

            # POST /sessions/<sid>/summarize — generate summary
            if path.startswith('/sessions/') and path.endswith('/summarize'):
                parts = path.split('/sessions/')
                sid = parts[1].replace('/summarize', '')
                summary = sm.summarize_session(sid)
                if summary:
                    self._respond(200, {"status": "ok", **summary})
                else:
                    self._respond(404, {"error": "session_not_found", "session_id": sid})
                return

            # POST /sessions/<sid>/delete — delete session
            if path.startswith('/sessions/') and path.endswith('/delete'):
                parts = path.split('/sessions/')
                sid = parts[1].replace('/delete', '')
                ok = sm.delete_session(sid)
                self._respond(200, {"status": "deleted" if ok else "not_found", "session_id": sid})
                return

        # MCP JSON-RPC POST endpoint
        if parsed.path == "/mcp" and self.command == "POST":
            body = self._read_body()
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                self._respond(400, {"error": "invalid_json"})
                return

            if isinstance(data, list):
                results = [self._handle_single_request(json.dumps(item).encode()) for item in data]
                self._respond(200, results)
            else:
                result = self._handle_single_request(body)
                self._respond(200, result)
        else:
            self._respond(404, {"error": "not_found"})


def main():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), MCPHTTPHandler)
    print(f"\n{'='*60}")
    print(f"  Insurance Sales MCP Server — HTTP Mode (R27)")
    print(f"  Port: {HTTP_PORT}")
    print(f"  Session CRUD API: {'✅ Enabled' if HAS_SESSION_MANAGER else '⚠️ Disabled'}")
    print(f"  Endpoints:")
    print(f"    POST /mcp     → JSON-RPC endpoint (accepts single + batch)")
    print(f"    GET  /health  → Health check")
    print(f"    GET/POST /sessions/* → Session CRUD (R27新增)")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSHUTDOWN...")
        server.server_close()


if __name__ == "__main__":
    main()
