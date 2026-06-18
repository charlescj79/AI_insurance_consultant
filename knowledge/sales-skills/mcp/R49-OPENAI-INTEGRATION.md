# OpenAI Agents SDK + hostedMcpTool 对接方案

**生成时间**: 2026-06-18 R49  
**适用MCP Server版本**: v1.3.0+ (protocolVersion=2024-11-05)  
**目标平台**: OpenAI Responses API + Agents SDK

---

## 一、对接架构

```
┌─────────────┐     hostedMcpTool      ┌──────────────┐
│ OpenAI       │ ─────────────────────▶ │ insurance-    │
│ GPT-5.5      │                        │ sales-mcp     │
│              │ ◀───────────────────── │ server        │
│ Agent SDK    │   MCP responses        │ (HTTP/8060)   │
└─────────────┘                        └──────────────┘
```

**关键路径**: `hostedMcpTool()` 将工具调用直接推送到 OpenAI Responses API，由OpenAI服务端发起MCP协议请求 → 我们的server.py → 返回结果给模型。

---

## 二、核心代码模板

### TypeScript/JavaScript (Node.js)

```typescript
import { Agent, hostedMcpTool } from '@openai/agents';

const insuranceAgent = new Agent({
  name: 'HKInsuranceAdvisor',
  instructions: `你是香港保险私域获客顾问。所有回答必须符合以下要求：
1. 遵守香港保监局GL-44准则
2. 不得做出任何未获批准的产品保证
3. 客户数据必须本地脱敏后查询
4. 分红收益表述必须使用"过往表现不代表未来"免责声明`,
  tools: [
    hostedMcpTool({
      serverLabel: 'insurance-sales-mcp',
      serverUrl: 'http://localhost:18060/mcp', // 或远程URL
      transport: 'http', // Streamable HTTP
    }),
    hostedMcpTool({
      serverLabel: 'compliance-engine', 
      serverUrl: 'http://localhost:18060/mcp',
    }),
  ],
});

// 使用Agent
const result = await insuranceAgent.run('客户A/B/C分级及需求诊断');
```

### Python

```python
import asyncio
from openai import OpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    # 方案A：通过LangChain adapter间接使用OpenAI模型
    client = MultiServerMCPClient({
        "insurance-mcp": {
            "transport": "http",
            "url": "http://localhost:18060/mcp",
        }
    })
    
    tools = await client.get_tools()
    
    # 方案B：直接通过OpenAI Responses API + tool_search
    openai_client = OpenAI()
    response = openai_client.responses.create(
        model="gpt-5.5",
        tools=[
            {"type": "web_search"},
            # MCP工具可通过function calling方式注入
        ],
        input="香港寿险市场最新趋势分析"
    )
    print(response.output_text)

asyncio.run(main())
```

---

## 三、我们的server.py对接兼容性分析

| server.py功能 | hostedMcpTool兼容 | 需要改造？ |
|--------------|-----------------|-----------|
| `/v1/tools/list` 端点返回工具列表 | ✅ 完全兼容 | ❌ 不需要 |
| HTTP Streamable传输 | ✅ 原生支持 | ❌ 不需要 |
| tool schema (JSON Schema) | ✅ OpenAI function calling格式映射 | ⚠️ 部分参数名可能需要camelCase转换 |
| protocolVersion=2024-11-05 | ✅ 最新稳定版兼容 | ❌ 不需要（非RC版本） |

---

## 四、合规部署建议

### 🟢 低风险模式：本地hostedMCP
```
GPT-5.5 ─── hostedMcpTool ──▶ localhost:18060 (我们的server)
```
- 数据不出本机
- 仅需审查agent instructions中的合规声明
- 推荐作为内部演示/demo用途

### 🟡 中风险模式：远程hostedMCP
```
GPT-5.5 ─── hostedMcpTool ──▶ cloud-hosted-server.example.com/mcp
```
**必须前置条件**:
1. 独立GL-44合规审查通过
2. 客户PII在发送到server前本地脱敏（session_manager.py已具备此能力）
3. Agent instructions中强制免责声明
4. audit_log记录所有MCP调用

---

## 五、部署步骤清单

1. [ ] `pip install @openai/agents` (npm) 或 `pip install openai langchain-mcp-adapters` (Python)
2. [ ] server.py部署到可访问地址（本地/Docker/Vercel）
3. [ ] 创建agent + hostedMcpTool配置
4. [ ] 合规审查：agent instructions + tool descriptions
5. [ ] 测试：运行10个典型查询验证合规响应
6. [ ] audit_log启用：记录所有工具调用

---

## 六、与现有产物映射

| 现有文件 | 对接用途 |
|---------|---------|
| `server.py` | MCP Server核心（提供tools/list + 执行） |
| `OPENAPI.json` | OpenAPI文档生成Swagger UI |
| `session_manager.py` | 客户数据脱敏+会话管理 |
| `compliance_trend_analysis` tool | GL-44合规扫描 |
| `gl34_compliance_check` tool | 分红保单治理 |

---

*R49产出 — 对接方案文档*
