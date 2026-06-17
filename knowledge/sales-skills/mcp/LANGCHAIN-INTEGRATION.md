# LangChain MCP Adapter Integration Guide

> 将保险咨询销售MCP Server对接到LangChain/LangGraph生态

## 核心原理

`langchain-mcp-adapters` (PyPI) 提供双向转换层，将我们的5个MCP工具转化为LangChain兼容的Tool对象。

```bash
pip install langchain-mcp-adapters
```

## 方式一：HTTP Transport（推荐用于生产）

### LangGraph Agent 集成

```python
import asyncio
from langchain_mcp_adapters.client import ConnectionClient
from langchain_core.tools import tool
from agents import Agent  # if using OpenAI Agents SDK

async def main():
    # Connect to our MCP server via HTTP
    async with ConnectionClient(
        transport="http",
        url="http://localhost:18060/mcp"
    ) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Use tools with LangGraph agent
        from langgraph.prebuilt import create_react_agent
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model="gpt-4o")
        graph = create_react_agent(llm, tools)
        
        result = await graph.ainvoke({
            "messages": [("user", "帮我查一下友邦的人寿危疾保条款")]
        })
        print(result["messages"][-1].content)

asyncio.run(main())
```

### 直接Tool调用

```python
from langchain_mcp_adapters.tools import MCPTool

# Create individual tool from our server
product_query = MCPTool(
    name="insurance_product_query",
    server_url="http://localhost:18060/mcp"
)

# Call directly
result = await product_query.ainvoke({
    "search_keyword": "重疾险",
    "detail": True
})
```

## 方式二：Dify可视化集成（无需编码）

### Dify设置 → Tool Providers → MCP

1. 打开 Dify → Settings → Tool Providers → MCP
2. 添加MCP Server:
   - Name: insurance-sales-mcp
   - Type: HTTP
   - URL: `http://your-server:18060/mcp`
3. Dify Agent自动发现5个工具并可用

## 方式三：OpenAI Agents SDK

```python
from agents import Agent, FunctionEventLog
from agents.mcp import MCPServerStreamableHttp

# Create MCP server connection
mcp_server = MCPServerStreamableHttp(
    "insurance-sales",
    url="http://localhost:18060/mcp"
)

# Use with agent
agent = Agent(
    name="InsuranceAdvisor",
    instructions="You are a Hong Kong insurance advisor...",
    mcp_servers=[mcp_server]
)

result = await agent.run("帮我比较保诚和友邦的重疾险")
```

## 方式四：OpenAI Responses API (远程MCP)

```python
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "tools": [{
      "type": "mcp",
      "server_label": "insurance-sales",
      "server_description": "HK Insurance Advisory MCP Server",
      "server_url": "http://your-server:18060/mcp"
    }],
    "input": ["帮我评估一个35岁男士的保险需求"]
  }'
```

## LangChain工具定义导出（供Dify/其他平台使用）

```python
# export_as_langchain_tools.py
from langchain_mcp_adapters.client import ConnectionClient

async def get_tools():
    async with ConnectionClient(
        transport="http",
        url="http://localhost:18060/mcp"
    ) as client:
        return await client.get_tools()

# 导出为JSON供Dify导入
import json, asyncio

tools = asyncio.run(get_tools())
print(json.dumps([{
    "name": t.name,
    "description": t.description,
    "parameters": t.input_schema
} for t in tools], indent=2, ensure_ascii=False))
```

## 安全配置

| 配置项 | 开发环境 | 生产环境 |
|--------|---------|---------|
| SERVER_API_KEY | 不设置(跳过) | 必须设置 |
| CORS_WHITELIST | 不设置(通配) | 明确域名列表 |
| HTTPS | 不需要 | nginx+TLS |
| Rate Limiting | 60/min | 建议20/min |

## 合规注意事项

1. **数据出境**: LangChain/LangGraph工具定义传输的是函数签名，不含PII数据
2. **本地执行**: 实际咨询处理在本MCP Server完成（香港境内）
3. **GL-44合规**: compliance_check工具在Agent流程中强制执行
4. **跨境红线**: RL-010规则确保不引导内地客户跨境投保
