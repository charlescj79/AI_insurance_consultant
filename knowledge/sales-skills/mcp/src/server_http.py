#!/usr/bin/env python3
"""
保险咨询销售 MCP Server — HTTP Transport Mode (R32 模块化)
===========================================================
协议: MCP JSON-RPC over HTTP POST + Session CRUD REST API
端口: 18060 (环境变量 SERVER_PORT 覆盖)
依赖: Python 3.7+ stdlib only

用法:
  python src/server_http.py              # default port 18060
  SERVER_PORT=9000 python src/server_http.py

⚠️ 安全提示：生产环境必须添加 API key 认证中间件
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.server import TOOL_HANDLERS, MCP_TOOLS

def handle_initialize():
    return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
            "serverInfo": {"name": "insurance-sales-mcp", "version": "1.2.0"}}

HTTP_PORT = int(os.environ.get("SERVER_PORT", "18060"))

class MCPHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def _read_body(self) -> bytes:
        cl = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(cl) if cl > 0 else b""

    def _respond(self, code: int, body: dict):
        resp = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def _handle_rpc(self, body_bytes: bytes) -> dict:
        try:
            msg = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            return {"error": {"code": -32700, "message": "Parse error"}}

        method = msg.get("method", "")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": handle_initialize()}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"tools": MCP_TOOLS}}
        if method == "tools/call":
            name = msg.get("params", {}).get("name", "")
            handler = TOOL_HANDLERS.get(f"handle_{name}")
            if not handler:
                return {"error": {"code": -32601, "message": f"Tool not found: {name}"}}
            try:
                result = handler(msg.get("params", {}).get("arguments", {}))
                return {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}
            except Exception as e:
                return {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": -32603, "message": str(e)}}
        return {"error": {"code": -32601, "message": f"Method not found: {method}"}}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == "/health":
            self._respond(200, {"status": "ok", "transport": "http", "port": HTTP_PORT})
        elif path == "/mcp/manifest":
            self._respond(200, {"name": "insurance-sales-mcp", "version": "1.2.0",
                "transport": "http", "endpoints": [{"path": "/mcp", "method": "POST"},
                {"path": "/health", "method": "GET"}]})
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        body_bytes = self._read_body()

        if parsed.path == "/mcp" and self.command == "POST":
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                return self._respond(400, {"error": "invalid_json"})
            if isinstance(data, list):
                results = [self._handle_rpc(json.dumps(item).encode()) for item in data]
                self._respond(200, results)
            else:
                self._respond(200, self._handle_rpc(body_bytes))
        else:
            self._respond(404, {"error": "not_found"})

def main():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), MCPHTTPHandler)
    print(f"\n{'='*60}")
    print(f"  Insurance Sales MCP Server — HTTP Mode (R32 Modular)")
    print(f"  Port: {HTTP_PORT}")
    print(f"  Endpoints:")
    print(f"    POST /mcp     → JSON-RPC (single + batch)")
    print(f"    GET  /health  → Health check")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSHUTDOWN...")
        server.server_close()

if __name__ == "__main__":
    main()
