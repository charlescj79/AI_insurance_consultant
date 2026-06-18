#!/usr/bin/env python3
"""
保险咨询销售 MCP Server — HTTP Transport Mode v2 (R53 安全加固版)
========================================================================
协议: MCP JSON-RPC over HTTP POST + Session CRUD REST API
端口: 18060 (环境变量 SERVER_PORT 覆盖)
认证: X-API-Key header (通过 SERVER_API_KEY 环境变量配置，生产环境必须设置)
速率限制: 60 req/min per IP

用法:
  SERVER_API_KEY=your-secret-key python src/server_http.py    # 推荐（带认证）
  python src/server_http.py                                    # 本地调试（无认证，开发环境仅）

环境变量:
  SERVER_API_KEY     - API密钥（生产环境必须设置，留空则禁用认证⚠️）
  SERVER_PORT        - 端口号 (default: 18060)
  CORS_WHITELIST     - 逗号分隔的允许Origin列表 (default: 全允许)
"""
import json, os, sys, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.server import TOOL_HANDLERS, MCP_TOOLS

# === 配置 ===
HTTP_PORT = int(os.environ.get("SERVER_PORT", "18060"))
API_KEY = os.environ.get("SERVER_API_KEY", "")
CORS_WHITELIST = [x.strip() for x in os.environ.get("CORS_WHITELIST", "").split(",") if x.strip()]

# === 速率限制器 ===
_rate_limit_map = {}  # ip -> [(timestamp, ...), ...]
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 60     # requests per window


def _check_rate_limit(ip: str) -> bool:
    """Return True if request is allowed."""
    now = time.time()
    _rate_limit_map.setdefault(ip, [])
    _rate_limit_map[ip] = [t for t in _rate_limit_map[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_map[ip]) >= RATE_LIMIT_MAX:
        return False
    _rate_limit_map[ip].append(now)
    return True


def handle_initialize():
    return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
            "serverInfo": {"name": "insurance-sales-mcp", "version": "1.3.0"}}


class MCPHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def _client_ip(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0]

    def _cors_headers(self):
        """Add CORS headers based on whitelist."""
        origin = self.headers.get("Origin", "")
        if CORS_WHITELIST:
            if origin and origin in CORS_WHITELIST:
                self.send_header("Access-Control-Allow-Origin", origin)
        # else: allow all (development mode)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")

    def _read_body(self) -> bytes:
        cl = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(cl) if cl > 0 else b""

    def _respond(self, code: int, body: dict):
        resp = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def _check_auth(self) -> bool:
        """Check API Key authentication. Return True if allowed."""
        if not API_KEY:
            # Dev mode: no auth required (only for local testing)
            return True
        key = self.headers.get("X-API-Key", "")
        if key == API_KEY:
            return True
        return False

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
            # Use tool name directly as key (fixed R53)
            handler = TOOL_HANDLERS.get(name)
            if not handler:
                return {"error": {"code": -32601, "message": f"Tool not found: {name}"}}
            try:
                result = handler(msg.get("params", {}).get("arguments", {}))
                return {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}
            except Exception as e:
                return {"error": {"code": -32603, "message": str(e)}}
        return {"error": {"code": -32601, "message": f"Method not found: {method}"}}

    def do_OPTIONS(self):
        self._respond(204, {})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if not self._check_auth():
            return self._respond(401, {"error": "unauthorized"})

        if path == "/health":
            self._respond(200, {
                "status": "ok",
                "transport": "http",
                "port": HTTP_PORT,
                "version": "1.3.0",
                "tools_count": len(MCP_TOOLS),
                "auth_enabled": bool(API_KEY),
            })
        elif path == "/mcp/manifest":
            self._respond(200, {
                "name": "insurance-sales-mcp",
                "version": "1.3.0",
                "transport": "http",
                "endpoints": [
                    {"path": "/mcp", "method": "POST"},
                    {"path": "/health", "method": "GET"},
                ],
                "auth": {"type": "x-api-key", "header": "X-API-Key"} if API_KEY else {"type": "none"},
            })
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        body_bytes = self._read_body()

        # Auth check for POST
        if not self._check_auth():
            return self._respond(401, {"error": "unauthorized"})

        # Rate limit check
        ip = self._client_ip()
        if not _check_rate_limit(ip):
            return self._respond(429, {"error": "rate_limit_exceeded", "retry_after": RATE_LIMIT_WINDOW})

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
        elif parsed.path == "/v1/execute" and self.command == "POST":
            # Unified execute endpoint (OpenAI-compatible)
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                return self._respond(400, {"error": "invalid_json"})
            if isinstance(data, list):
                results = [self._handle_rpc(json.dumps(item).encode()) for item in data]
                self._respond(200, {"results": results})
            elif "tool" in data:
                # OpenAI-style single tool call
                tool_name = data["tool"]
                tool_args = data.get("arguments", {})
                result = TOOL_HANDLERS.get(tool_name, lambda _: {"error": "unknown_tool"})(tool_args)
                self._respond(200, {"result": result})
            else:
                return self._respond(400, {"error": "missing tool field"})
        else:
            self._respond(404, {"error": "not_found"})


def main():
    print(f"\n{'='*60}")
    print(f"  Insurance Sales MCP Server — HTTP Mode (R53 Secure)")
    print(f"  Port: {HTTP_PORT}")
    print(f"  Auth: {'ENABLED' if API_KEY else 'DISABLED (dev mode)'}")
    print(f"  Rate Limit: {RATE_LIMIT_MAX}/min per IP")
    print(f"  Endpoints:")
    print(f"    POST /mcp      → JSON-RPC (single + batch)")
    print(f"    POST /v1/execute → Unified execute")
    print(f"    GET  /health   → Health check")
    print(f"    GET  /mcp/manifest → Server manifest")
    if API_KEY:
        print(f"\n  ⚠️  API_KEY enabled. Set SERVER_API_KEY env var to configure.")
    print(f"{'='*60}\n")

    server = HTTPServer(("0.0.0.0", HTTP_PORT), MCPHTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSHUTDOWN...")
        server.server_close()


if __name__ == "__main__":
    main()
