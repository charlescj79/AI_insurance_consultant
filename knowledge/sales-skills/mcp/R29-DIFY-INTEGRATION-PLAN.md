# Dify Integration Plan — Insurance Sales MCP Server

**Round**: R29 | Date: 2026-06-17 | Priority: P1 (High)

## 1. Platform Overview

Dify is an open-source AI application development platform with **native bidirectional MCP support** (client + server). GitHub 131k+ stars, active community, supports private deployment.

### Key Facts (verified via web_search):
- Dify has released community-built **MCP Server plugin** that converts Dify apps into MCP-compliant services
- Dify is building **native MCP support** for publishing Dify apps as MCP servers with one click
- Supports running MCP plugins in private network environments only (security recommendation)
- Integration path: Dify App → MCP Plugin → External MCP clients

### Why P1 Priority:
1. 国内可私有部署，合规风险最低（境内数据不出境）
2. 可视化工作流引擎支持多步骤保险咨询流程编排
3. MCP双向支持使我们的Server既能消费Dify工具也能被Dify引用

## 2. Integration Architecture

```
┌─────────────────┐    MCP JSON-RPC     ┌──────────────────────┐
│  Dify App       │◄══════════════════►│  Insurance Sales     │
│  (Insurance AI) │   Streamable HTTP  │  MCP Server          │
│                 │                    │  (our product)       │
└─────────────────┘                    └──────────────────────┘
                                              │
                                         ┌────────┐
                                         │ KB     │
                                         │ DB +   │
                                         │ RL-010 │
                                         │ GL-44  │
                                         └────────┘
```

### Data Flow:
1. User query enters Dify App (insurance workflow)
2. Dify calls our MCP Server via SSE endpoint (`/v1/tools/{name}/call`)
3. MCP Server runs compliance_check → product_query → objection_handler chain
4. Compliance-passed response returns to Dify for refinement
5. Final output rendered in Dify's UI / API

## 3. Implementation Steps

### Step 1: Prepare our server as MCP Client (consume Dify tools) ⏳ TODO
```bash
pip install langchain-mcp-adapters
python -c "
from langchain_mcp_adapters.client import MultiServerMCPClient
client = MultiServerMCPClient(
    providers={
        'insurance': {
            'command': 'python3',
            'args': ['/path/to/server_http_r27.py'],
            'transport': 'streamable_http',
            'url': 'http://localhost:18060/v1/tools/list'
        }
    }
)
tools = await client.get_tools()
"
```

### Step 2: Prepare our server as MCP Server (expose to Dify via plugin) ⏳ TODO
- Convert `server_http_r27.py` MCP endpoints into standard MCP JSON-RPC format
- Implement `initialize`, `tools/list`, `tools/call` MCP protocol methods
- Support SSE transport for Dify compatibility

### Step 3: Deploy Dify private instance (recommended)
```yaml
# docker-compose.yml for Dify + Insurance MCP
version: "3.8"
services:
  dify-api:
    image: langgenius/dify-api:1.0.0
    environment:
      - CONSOLE_WEB_URL=https://dify.internal
      - SERVICE_API_URL=https://api.dify.internal
    volumes:
      - ./data:/app/api/data

  dify-web:
    image: langgenius/dify-web:1.0.0
    environment:
      - CONSOLE_API_URL=https://api.dify.internal

  insurance-mcp:
    build: ../mcp/
    ports: ["18060:18060"]
    environment:
      - SERVER_TRANSPORT=http
      - SERVER_PORT=18060
```

## 4. Compliance Analysis

| Risk Factor | Level | Notes |
|-------------|-------|-------|
| 数据出境 | ✅ NONE | Dify私有部署境内，数据不离开中国大陆 |
| PII处理 | ⚠️ MEDIUM | 需配置Dify的PII脱敏插件 |
| GL-44对齐 | ✅ COMPLIANT | MCP Server内置RL-010合规规则库(7条跨境销售话术红线) |
| 保险咨询资质 | ❌ BLOCKING | Dify上的AI不能替代持牌顾问，必须加免责声明 |
| 跨境资金引导 | ❌ BLOCKING | AI回复不得涉及跨境转账指导 |

### Compliance Requirements for Dify deployment:
1. **必加声明**: "本服务提供保险资讯参考，不构成保险投资建议。最终投保决定须由持牌顾问在港境内完成。"
2. **必须配置**: PII脱敏(保单号/身份证号等自动mask)
3. **必须配置**: 跨境销售话术拦截(RL-010规则库作为Dify插件前置过滤)
4. **不建议部署于**: Coze/扣子(字节跳动境内服务器)，合规风险与Dify相同但更复杂

## 5. Risk Assessment Summary

| Aspect | Rating | Details |
|--------|--------|---------|
| Technical feasibility | HIGH | Dify MCP plugin成熟，有社区实践案例 |
| Deployment cost | LOW | Docker私有部署，单台服务器即可 |
| Compliance risk | LOW (with private deployment) | 境内数据不出境 |
| Time to MVP | ~2 days | Config + test + compliance review |

## 6. Alternative: Coze/扣子 Analysis

**Verdict**: ⚠️ Conditional approval only for education content, NOT for insurance sales guidance.

- Pros: Strong distribution, large Chinese user base
- Cons: 境内服务器处理保险数据=跨境数据合规灰色地带；字节跳动数据策略不可控
- Recommendation: Use Dify self-hosted for all insurance-related AI; use Coze only for general insurance科普(非销售导向)

## 7. Next Actions (R30)

1. ✅ Write this integration plan
2. ⏳ Create Dify MCP plugin manifest (server-card format per MCP spec SEP-1730)
3. ⏳ Deploy test Dify instance (local Docker) for validation
4. ⏳ Test MCP bidirectional connectivity
5. ⏳ Compliance review of Dify workflow output

---

**Status**: Plan complete, implementation pending R30-R31.
**Dependencies**: Docker Desktop required for local testing; GitHub repo needed for sharing.
