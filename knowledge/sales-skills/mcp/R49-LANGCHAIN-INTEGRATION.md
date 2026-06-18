# LangChain MCP Adapters 接入指南

**生成时间**: 2026-06-18 R49  
**目标库**: `langchain-mcp-adapters` (PyPI) + `langchain-mcp-tools` (第三方)  
**适用MCP Server版本**: v1.3.0+ (兼容协议2025-03-26 / 2024-11-05)

---

## 一、安装

```bash
pip install langchain-mcp-adapters
# 或
pip install langchain-mcp-tools   # 第三方库（功能更强，含convert_mcp_to_langchain_tools）
```

---

## 二、核心对接代码

### 方案A：MultiServerMCPClient (LangChain官方)

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langgraph.prebuilt import create_react_agent

async def main():
    # 连接我们的insurance-mcp server
    client = MultiServerMCPClient({
        "insurance-sales": {
            "transport": "http",           # Streamable HTTP
            "url": "http://localhost:18060/mcp",
        },
        # 可同时连接其他MCP server
        # "brave-search": {
        #     "transport": "stdio",
        #     "command": "npx",
        #     "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        #     "env": {"BRAVE_API_KEY": "your-key"},
        # }
    })
    
    # 获取工具列表并转换为LangChain兼容格式
    tools = await client.get_tools()
    
    # 创建Agent
    agent = create_agent(
        model="claude-sonnet-4-6",
        tools=tools,
    )
    
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "分析香港重疾险市场需求"}]
    })
    print(result)

asyncio.run(main())
```

### 方案B：langchain-mcp-tools (第三方，功能更强)

```python
from langchain_mcp_tools import convert_mcp_to_langchain_tools
import asyncio

async def main():
    tools = await convert_mcp_to_langchain_tools({
        "insurance-sales": {
            "command": "python",
            "args": ["/path/to/server.py"],
            "transport": "stdio",
        }
    })
    
    # 返回可直接传入LangChain Agent的tools列表
    print(f"Available tools: {[t.name for t in tools]}")

asyncio.run(main())
```

---

## 三、LangGraph Agentic工作流集成

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langgraph.graph.add_messages import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# 构建LangGraph工作流
workflow = StateGraph(AgentState)

# 添加节点（含MCP工具）
workflow.add_node("insurance_agent", create_react_agent(model, tools))

# 连接边
workflow.add_edge(START, "insurance_agent")
workflow.add_edge("insurance_agent", END)

app = workflow.compile()

# 运行
result = app.invoke({
    "messages": [("user", "客户A需求诊断：35岁已婚，年入200万港币")]
})
```

---

## 四、Dify MCP Server模式集成

### Dify作为MCP Server暴露保险工具

在Dify v1.6+中，我们的server.py可作为外部MCP Server被Dify调用：

```python
# Dify MCP Manifest (JSON)
{
    "name": "insurance-sales-mcp",
    "version": "1.3.0",
    "transport": "http",
    "url": "http://localhost:18060/mcp",
    "protocolVersion": "2024-11-05",
    "tools": [
        {"name": "insurance_product_query"},
        {"name": "compliance_check"},
        {"name": "needs_assessment"},
        {"name": "objection_handler"},
        {"name": "private_sop_runner"},
        ...
    ]
}
```

在Dify workflow中通过MCP节点直接引用。

---

## 五、协议兼容性确认

| 我们的server.py | LangChain adapter支持 | 状态 |
|---------------|---------------------|------|
| protocolVersion=2024-11-05 | ✅ 兼容（adapter支持2025-03-26 + 向后兼容） | OK |
| stdio传输 | ✅ MultiServerMCPClient transport="stdio" | OK |
| HTTP传输 | ✅ transport="http" (Streamable) | OK |
| tool schema (JSON Schema) | ✅ convert_mcp_to_langchain_tools解析 | OK |

---

## 六、部署步骤

1. [ ] `pip install langchain-mcp-adapters` 
2. [ ] server.py可用（stdio或HTTP模式）
3. [ ] 编写agent config（见上方代码模板）
4. [ ] 本地测试所有11个工具是否可被调用
5. [ ] 合规审查：验证GL34合规引擎在LangChain上下文中正常触发

---

*R49产出 — LangChain接入指南*
