# Insurance Sales Advisory MCP Server v2.0

> 香港保险咨询 AI 代理 — GL-44 & RL-010 合规 | 10 MCP Tools | Apache-2.0

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: ≥3.9](https://img.shields.io/badge/python-%E2%89%A53.9-blue.svg)](https://www.python.org/)
[![MCP Version](https://img.shields.io/badge/MCP-v2.0-green)](https://modelcontextprotocol.io/)

## 🏠 Overview

Production-grade MCP (Model Context Protocol) server providing **10 insurance advisory tools** for Hong Kong insurance consulting workflows. Built for developers, integrators, and licensed insurance professionals.

### Why This Server?

| Feature | Description |
|---------|-------------|
| **GL-44 Compliant** | All outputs include HKIA GL-44 required disclosures |
| **RL-010 Cross-border Protection** | 7 red-line checks prevent unauthorized mainland sales |
| **PII Auto-masking** | Policy numbers, IDs, phone numbers automatically masked |
| **Dual Transport** | stdio (local) + HTTP SSE (remote) for any integration |
| **Session Isolation** | Configurable TTL with automatic data purge |
| **Open-source** | Apache-2.0 — free for commercial use |

## 📦 Quick Start

### Install via pip

```bash
pip install insurance-sales-mcp
```

### Claude Desktop / Cursor / Windsurf (stdio)

```json
{
  "mcpServers": {
    "insurance-sales": {
      "command": "python3",
      "args": ["-m", "insurance_sales_mcp"],
      "transport": "stdio"
    }
  }
}
```

### Docker (HTTP SSE)

```bash
docker run -p 18060:18060 ghcr.io/your-org/insurance-sales-mcp:latest
# Health check: curl http://localhost:18060/health
```

### OpenAI Responses API

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-5.5",
    tools=[{
        "type": "mcp",
        "server_label": "insurance-sales",
        "server_description": "HK Insurance Sales Advisory — GL-44 & RL-010 Compliant",
        "server_url": "https://your-server.example.com/mcp",
        "require_approval": "never"
    }],
    input=[{"role": "user", "content": "Compare term life plans for age 35"}]
)
```

### LangChain / LangGraph

```bash
pip install langchain-mcp-adapters
```

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "insurance-sales": {
        "transport": "http",
        "url": "https://your-server.example.com/mcp"
    }
})
tools = await client.get_tools()
```

## 🔧 10 MCP Tools (v2.0)

| # | Tool Name | Description | Compliance Coverage |
|---|-----------|-------------|---------------------|
| 1 | `insurance_product_query` | Product catalog + clause details with guaranteed/non-guaranteed markers | GL-44 RL-002, YL-001 |
| 2 | `compliance_check` | Full red-line + yellow-line scanning (14+7 rules) | GL-44 all rules |
| 3 | `client_intake` | Structured client data collection with PII auto-masking | PII protection |
| 4 | `needs_scoring` | Client needs classification A/B/C/D scoring engine | Session isolation |
| 5 | `objection_handler` | 6 objection types × 3-tier response (no guaranteed-return) | No prohibited language |
| 6 | `compliance_rewrite` | Auto-fix compliant text from flagged content | GL-44 auto-fix |
| 7 | `lifecycle_analyzer` | D0→D30 customer journey analysis with retention insights | — |
| 8 | `client_crm_tag` | CRM tag sync + client grading (A/B/C/D) | Session TTL purge |
| 9 | `multi_turn_dialogue` | Context manager for multi-turn sales dialogue (80-round window) | Conversation scope |
| 10 | `compliance_trend_analysis` | Violation pattern detection across sessions | Audit trail |

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health (tools_count, version) |
| POST | `/v1/tools/list` | List all 10 MCP tools with schemas |
| POST | `/v1/tools/{name}/call` | Call tool with arguments |
| POST | `/v1/execute` | Unified auto-dispatch endpoint |
| POST | `/v1/chat/completions` | OpenAI-compatible chat interface |
| GET/POST/PUT/DELETE | `/v1/sessions/*` | Session CRUD (full spec in OPENAPI.json) |

## 🏗 Architecture

```
┌─────────────┐    stdio     ┌──────────┐
│ Claude      │◄────────────►│          │
│ Desktop     │              │          │
└─────────────┘              │  MCP     │
┌─────────────┐    stdio     │  Server  │   HTTP SSE
│ Cursor /    │◄────────────►│  (10     │◄─────►  External APIs
│ Windsurf    │              │  Tools)  │
└─────────────┘              │          │
┌─────────────┐    MCP     │          │
│ OpenAI      │───────────►│          │   Streamable HTTP
│ Responses   │  (remote)  │          │
└─────────────┘              └──────────┘
┌─────────────┐    MCP     ┌──────────┐
│ LangChain / │───────────►│          │   langchain-mcp-adapters
│ LangGraph   │            │ Adapter  │
└─────────────┘            └──────────┘
```

## 🛡 Compliance Framework

### GL-44 Rules (Hard-coded)

| Rule | Description | Enforcement |
|------|-------------|-------------|
| RL-002 | 收益承诺禁则 — No guaranteed-return language | compliance_check + compliance_rewrite |
| YL-001 | 演示利率非保证标注 | insurance_product_query |
| YL-003 | 比较表需完整条件 | compliance_check |
| YL-005 | 风险提示必须清晰 | All output templates |

### RL-010 Cross-border Red Lines (7 Rules)

1. No direct sales promotion to mainland China residents
2. No encouragement for cross-border policy purchase
3. Physical presence in HK required for signing
4. Only licensed distributors may handle sales activities
5. No online payment processing from mainland accounts
6. No marketing targeted at mainland social media platforms
7. All output must include regulatory disclaimer

## 📁 Project Structure

```
insurance-sales-mcp/
├── server.py              # Core MCP stdio server (10 tools v2.0)
├── server_http_r27.py     # HTTP SSE transport mode
├── session_manager.py     # Multi-turn state tracker (80-round window)
├── kb_validator.py        # Knowledge base compliance validator
├── OPENAPI.json           # OpenAPI 3.0 spec (9 endpoints, 16 schemas)
├── test_mcp_suite.py      # Test suite
├── pyproject.toml         # Build config (setuptools)
├── setup.py               # Legacy packaging
├── docker-compose.yml     # Docker deployment
├── README.md              # This file
└── LICENSE                # Apache-2.0
```

## 🧪 Testing

```bash
# Run all tests
python test_mcp_suite.py

# Coverage
coverage run -m pytest test_mcp_suite.py
coverage report
```

## 📄 License

Apache-2.0 — See [LICENSE](LICENSE) for full text.

---

## ⚠️ Regulatory Disclaimer

> **This software is provided as a technical tool for insurance information reference only.**
> It does NOT constitute insurance advice, solicitation, or recommendation.
> All outputs must be reviewed by a licensed Hong Kong insurance intermediary before use.
>
> Per Cap. 41 Insurance Ordinance:
> - This tool does not constitute regulated activity under the Insurance Ordinance
> - Cannot be used to directly sell insurance products to mainland China visitors
> - All outputs require review by a licensed insurance intermediary
> - GL-44 / RL-010 cross-border sales red lines are strictly enforced

---

**Built for developers, licensed intermediaries, and compliant AI integration.** 🏛️🇭🇰
