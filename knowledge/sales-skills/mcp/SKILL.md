# Insurance Sales MCP Agent Skill

**Version**: 0.2.0 | **License**: Apache-2.0 | **Category**: Insurance / Financial Services

---

## Overview

An agentic skill that enables insurance advisors to use AI-powered compliance checking, product query, client needs assessment, objection handling, and SOP automation — all within the GL-44 regulatory framework.

This skill is designed for **licensed Hong Kong insurance intermediaries** who want to leverage MCP-compatible AI assistants (Claude Desktop, Cursor, VS Code, OpenAI Responses API) to streamline their daily workflow while maintaining strict regulatory compliance.

---

## When to Use This Skill

Use when you are:
- A licensed HK insurance advisor searching for product information
- Need to check sales material against GL-44 / GN16 compliance rules
- Preparing client needs assessment documentation
- Generating objection-handling scripts for common objections
- Running private SOP workflows (Day 0 to Day 7)

**Do NOT use when**: You are providing unlicensed insurance solicitation, selling directly to mainland China residents, or storing sensitive PII on remote/cloud servers.

---

## MCP Tools Available

| Tool | Description | Compliance Level |
|------|-------------|-----------------|
| `insurance_product_query` | Query HK insurance product clauses (list/detail) | LOW |
| `compliance_check` | 14 red-line + 4 yellow-line compliance engine | CRITICAL |
| `needs_assessment` | Client needs diagnosis + A/B/C/D grading | MEDIUM |
| `objection_handler` | Objection handling scripts (6 types × 3 levels) | MEDIUM |
| `private_sop_runner` | Private SOP Day-0~Day-7 workflow automation | MEDIUM |

---

## Setup Instructions

### Option 1: MCP Client (stdio) — Claude Desktop / Cursor / Windsurf

```json
{
  "mcpServers": {
    "insurance-sales": {
      "command": "python3",
      "args": ["/path/to/knowledge/sales-skills/mcp/server.py"],
      "env": {
        "SERVER_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Option 2: HTTP Transport — Remote Access

```bash
# Start the server (requires API_KEY)
export SERVER_API_KEY="your-secret-key"
export HTTP_PORT=18060
python3 knowledge/sales-skills/mcp/server_http_r27_auth.py
```

```json
{
  "mcpServers": {
    "insurance-sales": {
      "transport": "http",
      "url": "https://localhost:18060/mcp",
      "headers": {
        "X-API-Key": "${SERVER_API_KEY}"
      }
    }
  }
}
```

### Option 3: Docker Deployment

```bash
docker build -f knowledge/sales-skills/mcp/Dockerfile-mcp -t insurance-sales-mcp .
docker run -d --name insurance-mcp \
  -p 18060:18060 \
  -e SERVER_API_KEY="your-secret-key" \
  -e CORS_WHITELIST="https://your-domain.com" \
  insurance-sales-mcp:latest
```

---

## Usage Examples

### Example 1: Compliance Check Before Publishing Marketing Material

> User: "Check this marketing text for compliance issues: '这款产品年化收益6%，保本保息，远超银行存款'"

The tool will return:
- `RL-002 CRITICAL`: 保本保息 — direct promise of guaranteed returns (forbidden)
- `RL-011 strict`: 隐含收益暗示 — "远超银行存款" implies guaranteed performance
- `YL-001`: 绝对化用语 — "远超" is an absolute claim

### Example 2: Product Query

> User: "查询重疾险产品，预算每年3万"

The tool returns matching products from the HK insurance product database with clause summaries, coverage details, and pricing.

### Example 3: Client Needs Assessment

> User: "客户35岁，已婚有一名8岁小孩，年收入100万港元，已有医疗险，希望增加重疾险和储蓄险"

The tool generates a structured needs assessment report with A/B/C/D client grade and recommended coverage strategy.

---

## Compliance Framework (GL-44 + GN16)

### Red-Line Rules (CRITICAL — blocked on violation)
| Rule | Description |
|------|-------------|
| RL-001 | 产品宣传合规要求 |
| RL-002 | **禁止保本保息承诺** (GN16强化版, 2026-03-31生效) |
| RL-003 | 利益区分要求 |
| RL-004 | **跨境销售禁令** — 不得向内地客户直接销售 |
| RL-006 | 公平待客原则 |
| RL-008 | HKMA反洗钱要求 (2026-05更新) |
| RL-009 | 首年佣金上限70% / 30%分摊制 (2026-01-01生效) |
| RL-010 | **跨境红线** — 强制免责声明 |

### Yellow-Line Rules (MEDIUM — flagged on suggestion)
| Rule | Description |
|------|-------------|
| YL-001 | 避免绝对化用语 (GN16: 禁用"预期收益"等模糊话术) |
| YL-002 | 避免制造焦虑/紧迫感 |
| YL-003 | 赴港投保流程规范 (GN16: 全程录音留存≥7年) |
| YL-005 | GN16利益区分 + 指引34要求 |

### GN16 2026 New Rules (新增合规检查)
- **演示利率上限**: 港元保单≤6%, 非港元≤6.5% (RL-NEW-001)
- **三档展示要求**: 保证+最佳估算+悲观三档必须同时展示 (YL-NEW-002)
- **分红实现率**: GN16强制披露2010年后全部分红实现率 (RL-NEW-003)

---

## Safety & Security

### API Key Authentication (R31+)
All HTTP endpoints require `X-API-Key` or `Authorization: Bearer` header.
Rate limit: 60 req/min per IP.

### Data Handling
- PII data is masked before any external transmission
- Session TTL auto-expiry enabled
- No persistent storage of client data in logs
- Local deployment recommended for any PII processing

### Regulatory Disclaimer (REQUIRED on all outputs)
```
⚠️ 本工具仅为保险信息参考，不构成投资建议。最终决策须由香港持牌顾问作出。
This tool is not a substitute for licensed insurance advice. 
Final decisions must be made through authorized channels in Hong Kong.
```

---

## Platform Integration Status

| Platform | Status | Method |
|----------|--------|--------|
| Claude Desktop | ✅ stdio | MCP config |
| Cursor / Windsurf | ✅ stdio | MCP config |
| OpenAI Responses API | ⏳ R32对接 | `type: "mcp"` remote server |
| LangChain/LangGraph | ✅ 代码就绪 | `langchain-mcp-adapters` |
| Dify | ✅ Docker方案 | 双向MCP client/server |
| n8n | ✅ HTTP方案 | HTTP Request Node / Custom Node |
| GitHub Registry | ⏳ Pending | Awaiting repo creation |
| Glama.ai | ⏳ Pending | Awaiting repo creation |
| Smithery.ai | ⏳ Pending | Awaiting repo creation |
| Agensi.io | ⏳ SKILL.md ready | 8-point security scan |

---

## License

Apache-2.0 — See LICENSE file for full text.

**For licensed insurance intermediaries only.** Not intended for unlicensed solicitation or cross-border sales to mainland China residents.
