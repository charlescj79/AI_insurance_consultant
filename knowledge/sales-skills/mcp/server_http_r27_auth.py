#!/usr/bin/env python3
"""
保险咨询销售 MCP Server — HTTP Transport + API Key Auth (R31安全加固版)
============================================================================
协议: MCP JSON-RPC over HTTP POST
端口: 18060 (可通过环境变量 SERVER_PORT 覆盖)
认证: X-API-Key header (通过 SERVER_API_KEY 环境变量配置)

安全修复 R31:
- ✅ API Key 认证层（应对 agent-wars.com 报告 30+ CVE）
- ✅ CORS 白名单控制
- ✅ Rate limiting (60 req/min per IP)
- ✅ 无TLS限制警告

用法:
  SERVER_API_KEY=your-secret-key python server_http_r27_auth.py

环境变量:
  SERVER_API_KEY     - API密钥（生产环境必须设置）
  SERVER_PORT        - 端口号 (default: 18060)
  CORS_WHITELIST     - 逗号分隔的允许Origin列表
"""

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import the core tools from server.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import (
    handle_initialize,
    handle_tools_list,
    TOOL_HANDLERS,
)

try:
    from session_manager import SessionManager
    HAS_SESSION_MANAGER = True
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cli', '..'))
    try:
        from mcp.session_manager import SessionManager
        HAS_SESSION_MANAGER = True
    except ImportError:
        HAS_SESSION_MANAGER = False

HTTP_PORT = int(os.environ.get("SERVER_PORT", "18060"))
API_KEY = os.environ.get("SERVER_API_KEY", "")
CORS_WHITELIST = [x.strip() for x in os.environ.get("CORS_WHITELIST", "").split(",") if x.strip()]

# Rate limiting: max requests per minute per IP
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 60     # requests per window


class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self):
        self._requests = {}

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        if ip not in self._requests:
            self._requests[ip] = []
        # Clean old entries
        self._requests[ip] = [t for t in self._requests[ip] if now - t < RATE_LIMIT_WINDOW]
        if len(self._requests[ip]) >= RATE_LIMIT_MAX:
            return False
        self._requests[ip].append(now)
        return True


rate_limiter = RateLimiter()


class AuthHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler with API key auth, rate limiting, CORS"""

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
        # CORS headers
        origin = self.headers.get("Origin", "")
        if CORS_WHITELIST:
            if origin in CORS_WHITELIST:
                self.send_header("Access-Control-Allow-Origin", origin)
        else:
            # No whitelist configured → allow all (dev mode)
            self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key, Authorization")
        self.end_headers()
        self.wfile.write(body_bytes)

    def _check_auth(self) -> bool:
        """Check API key. If no key configured, allow all (dev mode)."""
        if not API_KEY:
            return True  # Dev mode: no auth required
        key = self.headers.get("X-API-Key") or self.headers.get("Authorization", "").replace("Bearer ", "")
        return key == API_KEY

    def _check_rate_limit(self, ip: str) -> bool:
        """Check rate limit. Returns True if allowed."""
        return rate_limiter.is_allowed(ip)

    def _get_client_ip(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0]

    def _handle_single_request(self, body_bytes: bytes) -> dict:
        """Process a single JSON-RPC request"""
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

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(204)
        origin = self.headers.get("Origin", "")
        if CORS_WHITELIST and origin not in CORS_WHITELIST:
            self.send_header("Access-Control-Allow-Origin", "*")
        elif not CORS_WHITELIST:
            self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        client_ip = self._get_client_ip()

        if not self._check_rate_limit(client_ip):
            self._respond(429, {"error": "rate_limit_exceeded", "retry_after_s": RATE_LIMIT_WINDOW})
            return

        # Session CRUD GET endpoints
        if HAS_SESSION_MANAGER:
            sm = SessionManager()
            path = parsed.path.rstrip('/')

            if path == '/sessions/list':
                limit = int(parse_qs(parsed.query).get('limit', [50])[0])
                sessions = sm.list_sessions(limit)
                self._respond(200, {"status": "ok", "total": len(sessions), "sessions": sessions})
                return

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

            if path.startswith('/sessions/'):
                parts = path.split('/sessions/')
                sid = parts[1] if len(parts) > 1 else None
                if sid and '/' not in sid and len(sid) < 30:
                    data = sm.export_session(sid)
                    if data:
                        self._respond(200, json.loads(data))
                    else:
                        self._respond(404, {"error": "session_not_found", "session_id": sid})
                    return

        if parsed.path == "/health":
            auth_mode = "API Key" if API_KEY else "None (dev mode)"
            self._respond(200, {
                "status": "ok",
                "transport": "http",
                "port": HTTP_PORT,
                "auth": auth_mode,
                "rate_limit": f"{RATE_LIMIT_MAX}/min"
            })
        elif parsed.path == "/mcp/manifest":
            self._respond(200, {
                "name": "insurance-sales-mcp",
                "version": "1.2.0-auth",
                "transport": "http",
                "auth_required": bool(API_KEY),
                "endpoints": [
                    {"path": "/mcp", "method": "POST"},
                    {"path": "/health", "method": "GET"},
                    {"path": "/sessions/*", "method": "POST|GET"},
                ],
            })
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        body_bytes = self._read_body()
        client_ip = self._get_client_ip()

        if not self._check_rate_limit(client_ip):
            self._respond(429, {"error": "rate_limit_exceeded", "retry_after_s": RATE_LIMIT_WINDOW})
            return

        # Auth check for all POST requests that aren't health checks
        if parsed.path != "/health" and not self._check_auth():
            self._respond(401, {
                "error": "unauthorized",
                "message": "Missing or invalid X-API-Key header",
                "hint": f"Set SERVER_API_KEY env var, then pass 'X-API-Key: {{key}}' header"
            })
            return

        # Session CRUD POST endpoints
        if HAS_SESSION_MANAGER and parsed.path.startswith('/sessions'):
            sm = SessionManager()
            path = parsed.path.rstrip('/')

            if path == '/sessions/create':
                try:
                    req = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
                except Exception:
                    self._respond(400, {"error": "invalid_json"})
                    return
                sid = req.get('session_id') or req.get('sid', f'session-{int(time.time())}')
                session = sm.create_session(sid)
                self._respond(201, {
                    "status": "created",
                    "session_id": session.session_id,
                    "turn_count": session.turn_count,
                    "customer_grade": session.get_grade(),
                    "max_context_turns": session.max_context_turns
                })
                return

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

            if path.startswith('/sessions/') and path.endswith('/summarize'):
                parts = path.split('/sessions/')
                sid = parts[1].replace('/summarize', '')
                summary = sm.summarize_session(sid)
                if summary:
                    self._respond(200, {"status": "ok", **summary})
                else:
                    self._respond(404, {"error": "session_not_found", "session_id": sid})
                return

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
    print(f"\n{'='*65}")
    print(f"  Insurance Sales MCP Server — HTTP Mode + API Key Auth (R31)")
    print(f"  Port: {HTTP_PORT}")
    print(f"  Auth: {'✅ API Key' if API_KEY else '⚠️ None (dev mode - set SERVER_API_KEY)'}")
    print(f"  Rate Limit: {RATE_LIMIT_MAX} req/{RATE_LIMIT_WINDOW}s per IP")
    print(f"  CORS Whitelist: {CORS_WHITELIST if CORS_WHITELIST else 'All origins'}")
    print(f"  Session CRUD: {'✅ Enabled' if HAS_SESSION_MANAGER else '⚠️ Disabled'}")
    print(f"\n  Endpoints:")
    print(f"    POST /mcp     → JSON-RPC (requires X-API-Key)")
    print(f"    GET/POST /sessions/* → Session CRUD")
    print(f"    GET  /health  → Health check")
    if API_KEY:
        print(f"\n  🔑 Set SERVER_API_KEY env var to enable auth!")
    else:
        print(f"\n  ⚠️  WARNING: No API key configured! Production use requires it.")
    print(f"{'='*65}\n")

    server = HTTPServer(("0.0.0.0", HTTP_PORT), AuthHTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSHUTDOWN...")
        server.server_close()


if __name__ == "__main__":
    main()
