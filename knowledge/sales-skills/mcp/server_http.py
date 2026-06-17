#!/usr/bin/env python3
"""
保险咨询销售 MCP Server — HTTP Transport Mode (R22 新增)
=========================================================
协议: MCP JSON-RPC over HTTP POST
端口: 18060 (可通过环境变量 SERVER_PORT 覆盖)
依赖: Python 3.7+ stdlib only (http.server + json)

用法:
  python server_http.py                     # default port 18060
  SERVER_PORT=9000 python server_http.py    # custom port

集成方式:
  # Claude Desktop / Cursor config — HTTP transport via MCP SDK proxy
  # OpenAI wrapper already handles this at AiBroker/openai_wrapper.py

安全说明:
  - 生产环境应加 TLS (nginx reverse proxy)
  - 当前无认证，仅限内网/本地开发使用
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Import the core tools from server.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import (
    handle_initialize,
    handle_tools_list,
    TOOL_HANDLERS,
)

HTTP_PORT = int(os.environ.get("SERVER_PORT", "18060"))


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler that accepts JSON-RPC requests"""

    def log_message(self, format, *args):
        # Silent logging (production: use proper logger)
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
        # Write all bytes at once to avoid partial writes
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
        
        # Session CRUD GET endpoints
        if HAS_SESSION_MANAGER:
            sm = SessionManager()
            path = parsed.path.rstrip('/')
            
            # GET /sessions/list — list all sessions
            if path == '/sessions/list':
                limit = int(parse_qs(parsed.query).get('limit', [50])[0])
                sessions = sm.list_sessions(limit)
                self._respond(200, {"status": "ok", "total": len(sessions), "sessions": sessions})
                return
            
            # GET /sessions/<sid> or GET /sessions/export?sid=X — export session
            if path.startswith('/sessions/'):
                sid = path.split('/sessions/')[1]
                data = sm.export_session(sid)
                if data:
                    self._respond(200, json.loads(data))
                else:
                    self._respond(404, {"error": "session_not_found", "session_id": sid})
                return
            
            # GET /sessions/summarize?sid=X — session summary
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
        
        if parsed.path == "/health":
            self._respond(200, {"status": "ok", "transport": "http", "port": HTTP_PORT})
        elif parsed.path == "/mcp/manifest":
            # Return MCP manifest (compatible with .mcpb format)
            self._respond(200, {
                "name": "insurance-sales-mcp",
                "version": "1.1.0",
                "transport": "http",
                "endpoints": [
                    {"path": "/mcp", "method": "POST"},
                    {"path": "/health", "method": "GET"},
                ],
            })
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/mcp" and self.command == "POST":
            body = self._read_body()
            # Check for batch requests (array of JSON-RPC)
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
    print(f"  Insurance Sales MCP Server — HTTP Mode")
    print(f"  Port: {HTTP_PORT}")
    print(f"  Endpoints:")
    print(f"    POST /mcp     → JSON-RPC endpoint (accepts single + batch)")
    print(f"    GET  /health  → Health check")
    print(f"    GET  /mcp/manifest → MCP manifest (.mcpb compatible)")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSHUTDOWN...")
        server.server_close()


if __name__ == "__main__":
    main()
