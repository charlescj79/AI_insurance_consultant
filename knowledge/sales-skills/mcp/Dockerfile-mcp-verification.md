# Dockerfile-mcp Verification Report

**Date**: 2026-06-17  
**Target**: `Dockerfile-mcp` for insurance-sales-mcp v2.0  
**Verdict**: ⚠️ **Has issues — needs correction**

---

## ✅ What's Correct

| Check | Status | Details |
|-------|--------|---------|
| Base image | ✅ | `python:3.11-slim` — appropriate for MCP server |
| WORKDIR | ✅ | `/app` — standard Python container convention |
| Dependencies | ✅ | `curl` installed for health check |
| pyproject.toml copy | ✅ | Build config included |
| setup.py copy | ✅ | Legacy packaging fallback |
| pip install | ✅ | `pip install --no-cache-dir .` reads pyproject.toml |
| Port exposure | ✅ | `EXPOSE 18060` matches server port |
| CMD (entry point) | ✅ | `CMD ["python3", "server_http_r27.py"]` — correct R27 HTTP server |
| docker-compose alignment | ✅ | Volumes, env vars, healthcheck all consistent |

---

## ❌ Issues Found

### Issue 1: Missing critical files (HIGH)

The Dockerfile only copies these Python files:
```
server.py, session_manager.py, kb_validator.py, openai_schema_adapter.py, gemini_config_generator.py
```

**Missing but required by the codebase:**
| File | Required By | Impact |
|------|------------|--------|
| `openai_mcp_integration_draft.py` | Not imported at runtime — **OK to skip** | Low (draft only) |
| `server_http.py` | Legacy HTTP mode — not used by CMD but may be needed for rollback | Medium |
| `test_mcp_suite.py` | Testing — can be skipped in prod, should add as separate volume | Low-Medium |

**Verdict**: No runtime-critical files are missing. The 5 copied files are the minimum required to run the server.

### Issue 2: Missing R30 v2.0 tool definitions check (MEDIUM)

The Dockerfile copies `server.py` which contains **all 10 tools** (Tools 1–10). Since `CMD` launches `server_http_r27.py`, we need to verify that file is also available in the container:

- ❌ **PROBLEM**: `server_http_r27.py` is NOT copied by any COPY statement!
- CMD references `server_http_r27.py` as the entry point
- But the COPY only includes: `server.py session_manager.py kb_validator.py openai_schema_adapter.py gemini_config_generator.py`

**This means the container will FAIL to start** — the CMD file won't exist in `/app`.

### Issue 3: Missing data directory (LOW)

The docker-compose.yml mounts `./data:/app/data` but the Dockerfile doesn't create the `/app/data` directory. This is not a hard failure (Docker will auto-create the mount point), but it's worth noting.

### Issue 4: HEALTHCHECK references wrong port path (MEDIUM)

```dockerfile
HEALTHCHECK ... CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:18060/health')" || exit 1
```

This depends on `server_http_r27.py` exposing `/health` at port 18060. **Confirmed working** per R29 test results (11/11 HTTP endpoints passed including health check).

---

## 🔧 Required Fix

### Fix for Issue 2: Add missing `server_http_r27.py` to COPY

The Dockerfile must copy `server_http_r27.py` since it's the CMD entry point:

**Current (broken):**
```dockerfile
COPY server.py session_manager.py kb_validator.py openai_schema_adapter.py gemini_config_generator.py ./
```

**Corrected:**
```dockerfile
COPY server.py server_http_r27.py session_manager.py kb_validator.py openai_schema_adapter.py gemini_config_generator.py ./
```

Or more defensively:
```dockerfile
COPY server*.py session_manager.py kb_validator.py openai_schema_adapter.py gemini_config_generator.py ./
```

### Fix for Issue 4 (Recommended): Use a separate healthcheck script

For clarity, the healthcheck should be extracted to its own file rather than inline:

```dockerfile
COPY healthcheck.py /usr/local/bin/healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python3 /usr/local/bin/healthcheck || exit 1
```

---

## 📋 Dockerfile Content Coverage Summary

| Component | Covered? | Details |
|-----------|----------|---------|
| **Core MCP server (server.py)** | ✅ Copied | All 10 tools v2.0 included |
| **HTTP server (server_http_r27.py)** | ❌ MISSING from COPY | CMD entry point — this is a critical bug |
| **Session Manager** | ✅ Copied | session_manager.py present |
| **KB Validator** | ✅ Copied | kb_validator.py present |
| **OpenAI Adapter** | ✅ Copied | openai_schema_adapter.py present |
| **Gemini Config Generator** | ✅ Copied | gemini_config_generator.py present |
| **OPENAPI spec** | ✅ Copied | OPENAPI.json at /app/ |
| **Build config** | ✅ Copied | pyproject.toml + setup.py |
| **All 10 MCP Tools** | ✅ Via server.py | All tool handlers defined in server.py |
| **Environment variables** | ⚠️ Set via docker-compose | SERVER_TRANSPORT, SERVER_PORT, CORS_ORIGINS |
| **Volume persistence** | ⚠️ Set via docker-compose | ./data:/app/data + ../cli/sessions:/app/sessions |

---

## ✅ Final Recommendation

1. **IMMEDIATE**: Add `server_http_r27.py` to the COPY directive (fixes Issue 2)
2. **RECOMMENDED**: Create `/app/data` directory in Dockerfile for volume mount clarity
3. **OPTIONAL**: Extract healthcheck command to a separate script file for readability

The Dockerfile is structurally sound and covers all necessary runtime components. The single blocking issue is the missing `server_http_r27.py` copy directive.
