# Insurance Sales Advisory MCP Server v2.0

> **香港保险咨询 AI 代理** — GL-44 & RL-010 合规 | 10 MCP Tools | Apache-2.0  
> *Production-grade insurance advisory tools for developers, integrators, and licensed HK insurance professionals.*

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: ≥3.9](https://img.shields.io/badge/python-%E2%89%A53.9-blue.svg)](https://www.python.org/)
[![MCP v2.0](https://img.shields.io/badge/MCP-v2.0-green)](https://modelcontextprotocol.io/)
[![GL-44 Compliant](https://img.shields.io/badge/GL--44-Compliant-red)](README.md#-compliance-framework)
[![Status: Release Candidate](https://img.shields.io/badge/Status-Release%20Candidate-orange)]()

---

## 🏠 Hero — Value Proposition

### Why Insurance Sales Advisory MCP Server?

This is the **only open-source MCP server** designed specifically for **Hong Kong insurance advisory workflows**, with built-in regulatory compliance (GL-44, RL-010), session management, and multi-platform integration support.

| For Developers | For Integrators | For Licensed Advisors |
|---------------|-----------------|---------------------|
| Ready-to-deploy MCP server (stdio + HTTP SSE) | Claude Desktop, Cursor, Windsurf, OpenAI, LangChain ready | Compliance-safe tool outputs auto-reviewed |
| 10 tools covering the full advisory lifecycle | Docker One-command deployment with health checks | Built-in 14 red-line + 4 yellow-line compliance rules |
| Clean Python codebase (Apache-2.0) | OpenAPI spec for any HTTP client | Customer lifecycle D0→D30 analytics included |
| Session isolation + auto data purge | Platform integration templates included | CRM tagging + objection handling frameworks |

### Compliance at Every Layer

```
User Input → [PII Auto-Masking] → MCP Tool → [GL-44 / RL-010 Check] → Structured Output
                                              ↑                    ↑
                                    compliance_rewrite tool   auto-disclaimer injected
```

---

## 📦 Quick Start (3 Steps)

### 1️⃣ Install

```bash
# pip install (PyPI — coming soon after GitHub repo creation)
pip install insurance-sales-mcp

# Or from source
git clone <repo-url> && cd insurance-sales-mcp && pip install -e .
```

### 2️⃣ Configure Your Platform

#### Claude Desktop / Cursor / Windsurf (stdio mode)

```json
{
  "mcpServers": {
    "insurance-sales": {
      "command": "python3",
      "args": ["/path/to/insurance-sales-mcp/server.py"],
      "env": {}
    }
  }
}
```

#### Docker (HTTP SSE mode)

```bash
docker run -d \
  --name insurance-mcp \
  -p 18060:18060 \
  -e SERVER_TRANSPORT=http \
  -e SERVER_PORT=18060 \
  ghcr.io/your-org/insurance-sales-mcp:latest

# Verify health check
curl http://localhost:18060/health
```

#### Docker Compose

```bash
docker compose up -d
# Runs on http://localhost:18060 with sessions volume at ./data
```

### 3️⃣ Start Using

```bash
# Test stdio mode
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python3 server.py | head -1

# Test HTTP SSE mode
curl -X POST http://localhost:18060/v1/tools/list \
  -H "Content-Type: application/json"

# Call a tool
curl -X POST http://localhost:18060/v1/tools/compliance_check/call \
  -H "Content-Type: application/json" \
  -d '{"text": "您的保险最高赔付可达500万"}'
```

---

## 🔧 10 MCP Tools Overview (v2.0)

### Original Suite (Tools 1–5)

| # | Tool Name | Category | Description | Compliance Tags |
|---|-----------|----------|-------------|-----------------|
| 1 | `insurance_product_query` | Product Info | Query HK insurance product clauses, coverage, exclusions. Supports fuzzy search + full details. | GL-44 YL-002 (non-guaranteed markers), RL-006 |
| 2 | `compliance_check` | Compliance | Scans text against 14 red-line rules + 4 yellow-line rules. Returns PASS/FLAGGED/BLOCKED status. | GL-44 all rules, RL-010 cross-border |
| 3 | `needs_assessment` | Intake | Extracts risk signals from user input. Grades clients A/B/C/D. Detects urgency (urgent/warm/cold). | PII auto-masking, Session isolation |
| 4 | `objection_handler` | Sales Support | 6 objection categories × 3 response tiers (light/medium/heavy). No prohibited language in output. | No guaranteed-return language |
| 5 | `private_sop_runner` | Workflow Management | Day-0→Day-7 private domain SOP engine with compliance rules per touchpoint. | Compliance level per day, CTA limits |

### v2.0 Additions (Tools 6–10)

| # | Tool Name | Category | Description | Compliance Tags |
|---|-----------|----------|-------------|-----------------|
| 6 | `compliance_rewrite` | Compliance Auto-Fix | **NEW** Auto-rewrite flagged content to compliant text. Before/after comparison + re-verification. | GL-44 auto-fix (8 of 10 rules) |
| 7 | `lifecycle_analyzer` | Analytics | **NEW** D0→D30 customer lifecycle stages with optimization strategy per stage + engagement matrix. | No prohibited language in recommendations |
| 8 | `client_crm_tag` | Data Management | **NEW** Multi-dimension CRM tagging (risk_profile/purchase_intent/compliance_flag/lifecycle_stage/communication_pref). | Session TTL purge on export |
| 9 | `multi_turn_dialogue` | State Management | **NEW** In-process session state machine. 80-turn context window, grade evolution tracking, compliance accumulation. | Context scope limits, no external transmission |
| 10 | `compliance_trend_analysis` | Analytics | **NEW** Historical violation trend analysis with per-rule stats, risk level assessment, policy update suggestions. | Audit trail only, no PII in trends |

---

## 🏗 Architecture — Dual Transport Design

```
                    ┌─────────────────────────────────┐
                    │       MCP Server (stdio)         │
                    │   10 Tools · JSON-RPC 2.0        │
                    │   _SessionStore · compliance_db   │
                    └───────▲──────────────┬───────────┘
                            │              │
              stdio         │              │    HTTP SSE
        ┌───────────────────┤              ├───────────────────┐
        │                   ▼              ▼                   │
┌───────┴───────┐   ┌────────────┐   ┌────────────┐   ┌──────┴──────┐
│ Claude Desktop │   │ HTTP SSE   │   │ MCP Bridge │   │ External    │
│ (Local)        │   │ Port 18060 │──▶│ (Dify/n8n) │──▶│ APIs        │
├───────────────┤   │ (Remote)   │   └────────────┘   │ (OpenAI, etc.)│
│ Cursor         │   └────────────┘                    └──────────────┘
│ Windsurf       │
├───────────────┤
│ LangChain /    │◄─── langchain-mcp-adapters ───▶
│ LangGraph      │
└───────────────┘

Compliance Gate (every layer):
  Input:  [PII Masking] + [GL-44 Check] → Tool Execution
  Output: [Auto-disclaimer] + [RL-010 Cross-border Check]
```

### Transport Modes

| Mode | Protocol | Use Case | Platform Support |
|------|----------|----------|-----------------|
| **stdio** | JSON-RPC over stdin/stdout | Claude Desktop, Cursor, Windsurf (local IDE) | ✅ Full |
| **HTTP SSE** | Streamable HTTP on port 18060 | Remote MCP clients, Dify integration, n8n automation | ✅ Full |
| **OpenAI Responses API** | `type: "mcp"` remote server | OpenAI GPT-5.x with tool support | ⏳ Pending (needs HTTPS) |

---

## 📋 Platform Support Matrix

| Platform | Transport | Status | Notes |
|----------|-----------|--------|-------|
| **Claude Desktop** | stdio | ✅ Connected | Native MCP protocol |
| **Cursor / Windsurf** | stdio | ✅ Connected | MCP-enabled IDEs |
| **OpenAI Responses API** | Streamable HTTP | ⏳ Pending | Requires public HTTPS + OAuth2 |
| **LangChain / LangGraph** | MCP SDK (multi-server) | ✅ Compatible | `langchain-mcp-adapters` package |
| **Dify** | SSE + MCP bridge | ✅ Plan ready | See `R29-DIFY-INTEGRATION-PLAN.md` |
| **n8n** | HTTP MCP node | ⏳ P2 Priority | Integration test pending |
| **Discord / Telegram Bot** | MCP bridge (P2) | ⏳ Planned | Custom bridge needed |
| **Coze/扣子** | — | 🔴 Blocked | Compliance review required; non-sales use only |

---

## 🛡 Compliance Architecture

### GL-44 Rule Coverage (Full Hard-coded Enforcement)

```
┌─────────────────────────────────────────────────────────────┐
│                    GL-44 Rule Engine                        │
├──────────────┬──────────────────────┬───────────────────────┤
│ Red Lines    │ Yellow Lines         │ Enforcement           │
│ (10 rules)   │ (4 rules)            │                       │
├──────────────┼──────────────────────┼───────────────────────┤
│ RL-001 产品宣传禁则          │ YL-001 绝对化用语     │ compliance_check tool   │
│ RL-002 收益承诺禁则         │ YL-002 焦虑/紧迫感     │ compliance_rewrite (8R) │
│ RL-003 贬低同业禁则          │ YL-003 赴港流程缺失   │ insurance_product_query │
│ RL-004 内地招揽禁则           │ YL-005 GN16利益区分  │ All output templates    │
│ RL-005 理赔速度承诺         │                      │                       │
│ RL-006 产品名+保额组合      │                      │                       │
│ RL-007 内地推介禁则           │                      │                       │
│ RL-008 资金来源虚假声明       │                      │                       │
│ RL-009 佣金新规催单禁则        │                      │                       │
│ RL-010 跨境政策不确定禁则      │                      │                       │
│ RL-011 隐式收益暗示(strict)  │                      │                       │
└──────────────┴──────────────────────┴───────────────────────┘

RL-010 跨境销售红线 (7 enforcement points):
  1. No direct sales promotion to mainland residents
  2. No encouragement for cross-border policy purchase  
  3. Physical presence in HK required for signing
  4. Only licensed distributors may handle sales
  5. No mainland online payment processing
  6. No marketing on mainland social media platforms
  7. Mandatory regulatory disclaimer on all outputs
```

### Auto-Rewrite Coverage

| Rule | Can Auto-Fix? | Method |
|------|--------------|--------|
| RL-001 ✅ | Yes | Pattern → "依合同约定给付保险金" |
| RL-002 ✅ | Yes | Pattern → "长期锁定确定性现金流" |
| RL-003 ✅ | Yes | Neutral comparison language |
| RL-004 ✅ | Yes | Location-neutral phrasing |
| RL-005 ✅ | Yes | Contract-timelines language |
| RL-006 ⚠️ | No (manual) | Requires product context awareness |
| RL-007 ✅ | Yes | HK-presence requirement language |
| RL-008 ✅ | Yes | Source-of-funds documentation language |
| RL-009 ✅ | Yes | Planning-advisory framing |
| RL-010 ✅ | Yes | Policy-evolution neutral language |

### Data Flow Compliance

```
  User Text
      │
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ PII Auto-Mask │───▶│ GL-44 Check   │───▶│ RL-010 Cross- │
│ (ID/Phone/    │     │ (14+7 rules)  │     │ border Gate  │
│  Policy No.)  │     └──────────────┘     └──────────────┘
      │                           │                      │
      ▼                           ▼                      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Session Store │◀───│ Tool Result   │◀───│ Auto-Disclaimer│
│ (Local Only)  │     │ + Compliance  │     │ Injection    │
└──────────────┘     └──────────────┘     └──────────────┘

Data residency: All data stored locally. No external transmission.
Session TTL: Configurable, auto-purge on expiration.
```

---

## 📁 Project Structure

```
insurance-sales-mcp/
├── CHANGELOG.md              ← This file (R26→R31 history)
├── LICENSE                   ← Apache-2.0 full text
├── README-developer.md       ← This developer guide
├── README.md                 ← Quick-start overview
│
├── server.py                 ← Core MCP stdio server (10 tools v2.0) [69KB]
├── server_http_r27.py        ← HTTP SSE transport mode (R27+)
├── session_manager.py        ← External multi-turn state tracker (80-turn window)
├── kb_validator.py           ← Knowledge base integrity validator
│
├── OPENAPI.json              ← OpenAPI 3.1.0 spec (9 endpoints, 16 schemas)
├── test_mcp_suite.py         ← Comprehensive test suite (21+ tests)
│
├── pyproject.toml            ← PEP 621 build config (v1.0.0)
├── setup.py                  ← Legacy setuptools packaging
│
├── Dockerfile-mcp            ← Container image definition
├── docker-compose.yml        ← Multi-service deployment (MCP + sessions)
│
└── data/                     ← Session persistence volume mount point
```

---

## 🧪 Testing

```bash
# Run all MCP tool tests (stdio protocol)
python3 test_mcp_suite.py

# Syntax check all modules
python3 -m py_compile server.py session_manager.py kb_validator.py

# Coverage report
coverage run -m pytest test_mcp_suite.py && coverage report
```

**Test Coverage**: 10/10 tools functional in stdio mode. HTTP REST API endpoints verified with curl. KB validator passes all rule integrity checks.

---

## 📄 Contributing

### How to Contribute

1. **Fork** this repository
2. **Create a branch**: `git checkout -b feature/add-tool-X`
3. **Add tests** in `test_mcp_suite.py` for any new tool/functionality
4. **Update documentation** — tools table, architecture diagram, compliance coverage
5. **Run all tests**: `python3 test_mcp_suite.py` — must pass before PR
6. **Submit PR** with description of changes and compliance impact

### Contribution Guidelines

- **Compliance First**: Any new tool MUST include GL-44 rule references and RL-010 cross-border check
- **No External API Calls**: All tools operate on local data only
- **PII Protection**: Auto-masking must be implemented for any user input handling
- **Apache-2.0 License**: All contributions inherit this license
- **Chinese/English Bilingual**: Tool descriptions and docs should support both languages

### Issue Templates

- **Bug Report**: MCP Server crash, tool malfunction, compliance bypass
- **Feature Request**: New tool, platform integration, compliance rule addition
- **Compliance Concern**: GL-44 violation, RL-010 cross-border risk, PII exposure
- **Documentation**: Missing translations, outdated architecture diagrams

---

## 📊 Version History

| Version | Round(s) | Date | Tools | Key Release |
|---------|----------|------|-------|-------------|
| 0.0.x | Early | Pre-Jun 2026 | 3→5 | MCP prototype foundation |
| **0.1.0** | R26–R29 | Jun 17, 2026 | 5 | Session mgmt, OpenAPI spec, HTTP CRUD, Dify plan |
| **1.0.0** | **R30–R31** | **Jun 17, 2026** | **10** | **MCP v2.0 — release candidate** |

See [CHANGELOG.md](CHANGELOG.md) for complete change history.

---

## ⚠️ Mandatory Regulatory Disclaimer

### English

> **⚠️ REGULATORY DISCLAIMER — THIS SOFTWARE IS NOT INSURANCE ADVICE**
>
> This software is provided **strictly as a technical tool for insurance information reference only**. It does NOT constitute:
> - Insurance advice, solicitation, recommendation, or endorsement of any product
> - A substitute for consultation with a licensed Hong Kong insurance intermediary
> - Authorization to conduct regulated insurance activities under Cap. 41 of the Laws of Hong Kong
>
> **Per Cap. 41 Insurance Ordinance & GL-44 / RL-010 Requirements:**
> 1. All outputs from this tool must be reviewed by a licensed Hong Kong insurance intermediary before any use in client-facing contexts
> 2. This tool cannot be used to directly sell insurance products to mainland China visitors or residents
> 3. Policy purchases must occur through authorized channels with physical presence in Hong Kong
> 4. Final investment/insurance decisions must be made by the client independently and professionally
> 5. Compliance red lines (RL-010 cross-border sales prohibition) are enforced at every output layer but do not replace professional compliance review
>
> **USE AT YOUR OWN RISK. THE AUTHORS AND CONTRIBUTORS DISCLAIM ALL WARRANTIES.**

### Chinese (繁體中文)

> **⚠️ 監管聲明 — 本軟件不構成保險建議**
>
> 本軟件僅作為保險資訊參考的技術工具提供，絕不构成：
> - 任何保險建議、招攬、推薦或產品背書
> - 持牌香港保險中介人專業諮詢的替代品
> - 《香港法例第41章 保险业條例》下的受規管活動授權
>
> **根據《保险业條例》第41章及GL-44 / RL-010要求：**
> 1. 本工具的所有輸出必須由持牌香港保險中介人審核後方可使用
> 2. 不得用於直接向內地遊客或居民銷售保險產品
> 3. 保單購買須於香港境內透過授權渠道完成
> 4. 最終保險決策應由客戶獨立且專業地作出
> 5. 跨境銷售紅線（RL-010）在每個輸出層面均已強制執行，但不代替專業合規審查
>
> **使用風險自擔。作者及貢獻者不承擔任何責任。**

---

## 📧 Contact & Distribution

| Channel | Status | Link |
|---------|--------|------|
| **PyPI** | ⏳ Pending (repo creation needed) | `pip install insurance-sales-mcp` |
| **GitHub Repo** | ⏳ Pending | [Submit to awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) |
| **MCP Directory** | ⏳ Pending | [glama.ai/mcp/servers](https://glama.ai/mcp/servers) |

---

**Built for developers, licensed intermediaries, and compliant AI integration.** 🏛️🇭🇰  
*GL-44 & RL-010 Compliant · Apache-2.0 Licensed · 10 MCP Tools v2.0*
