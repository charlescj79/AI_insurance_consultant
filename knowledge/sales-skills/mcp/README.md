# AI Insurance Consultant — MCP Server + CLI + Agentic Platform
# 香港保险私域获客：公域内容引流 → 私域需求挖掘 → 合规预约咨询

## 📁 Repository Layout

```
knowledge/sales-skills/mcp/
├── src/                    # Production code (R32 modular)
│   ├── server.py           # stdio MCP entry (~128 lines)
│   ├── server_http.py      # HTTP transport (~107 lines)
│   └── tools/              # 10 tools, each < 150 lines
├── cli/                    # CLI v7.1 (independent)
├── compliance/             # GL-44 / GN16 rules
├── specs/                  # MCP tool JSON schemas
├── docs/                   # Documentation
├── tests/                  # Unit + integration tests
├── .agents.md              # AI tools navigation guide
├── TASK-BOARD.md           # OpenClaw task queue (cron reads this)
├── pyproject.toml          # PyPI package config
├── Dockerfile-mcp          # Container build
├── docker-compose.yml      # Local dev
├── LICENSE                 # MIT License
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install (PyPI / uvx)
```bash
pip install .          # or: uvx insurance-mcp
```

### 2. MCP Client Configuration (Claude Desktop / Cursor)
```json
{
  "mcpServers": {
    "insurance-sales": {
      "command": "python3",
      "args": ["path/to/src/server.py"]
    }
  }
}
```

### 3. HTTP Server
```bash
cd src
python server_http.py  # default port 18060
```

## 🔧 10 MCP Tools

| # | Tool | Purpose |
|---|------|---------|
| 1 | `insurance_product_query` | Product clause search |
| 2 | `compliance_check` | GL-44/GL34 red/yellow line scanner |
| 3 | `needs_assessment` | Customer needs diagnosis (grade A-D) |
| 4 | `objection_handler` | Objection handling scripts (6 cat, 3 tiers) |
| 5 | `private_sop_runner` | Day-0 to Day-7 private domain SOP |
| 6 | `compliance_rewrite` | Auto compliance fix for违规 content |
| 7 | `lifecycle_analyzer` | D0-D30 customer journey analysis |
| 8 | `client_crm_tag` | Multi-dimensional CRM tagging |
| 9 | `multi_turn_dialogue` | Multi-turn context manager (80-turn window) |
|10 | `compliance_trend_analysis` | Compliance history trend + violation patterns |

## 📐 Architecture Principles

- **Modular**: Each tool in its own file (< 150 lines)
- **Dual transport**: stdio (Claude Desktop) + HTTP (Dify/Discord/external)
- **Compliance-first**: GL-44 / GN16 rules baked in, never bypassed
- **OpenClaw-native**: TASK-BOARD.md driven task queue for cron automation

## 🔄 OpenClaw Harness

Cron reads `TASK-BOARD.md` → picks next `[ ]` task → executes via subagent → updates board status. Each run does exactly one small task. No context overflow.

## 📜 License

MIT License — see LICENSE file

---

Built by CJ / charlescj79 · Insurance MCP Platform v2.0
