# LangChain MCP Adapter Integration — insurance-sales-mcp

**Created**: 2026-06-17 (R32)
**Status**: Integration draft ready for testing

---

## Overview

This guide shows how to connect our `insurance-sales-mcp` HTTP server with LangChain's `langchain-mcp-adapters` and `langchain-mcp-client` packages, enabling the 5 MCP tools to be used inside LangGraph agents.

---

## Prerequisites

```bash
pip install langchain-mcp-adapters langchain-mcp-client langgraph openai
# or for TypeScript:
npm install @langchain/mcp-adapters @langchain/openai
```

---

## Method 1: LangGraph Agent (HTTP Transport) — Production Recommended

```python
"""
insurance-sales-mcp — LangGraph Integration via HTTP transport
Usage: python langchain_integration.py
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio

async def main():
    # Connect to our MCP server (HTTP transport)
    mcp_client = MultiServerMCPClient({
        "insurance-sales": {
            "transport": "http",
            "url": "http://localhost:18060/mcp",  # or your HTTPS endpoint
            "headers": {
                "X-API-Key": "${SERVER_API_KEY}"  # from env var
            } if False else None,  # Set to True when using real API key
        }
    })
    
    # Get tools from MCP server
    tools = await mcp_client.get_tools()
    
    print(f"Loaded {len(tools)} tools from insurance-sales-mcp:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")
    
    # Create LangGraph agent with our tools
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    agent = create_react_agent(llm, tools)
    
    # Test: product query
    result = agent.invoke({
        "messages": [("user", "查询香港储蓄险产品，年缴10万，保20年")]
    })
    print("\nAgent response:", result["messages"][-1].content)
    
    # Cleanup
    await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Method 2: LCEL Chain with MCPTool (Simpler, No Agent Loop)

```python
"""
insurance-sales-mcp — LCEL Chain Integration
"""

from langchain_mcp_adapters.tools import MCPTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import asyncio

async def main():
    # Create individual tool instances
    product_tool = MCPTool(
        server="insurance-sales",
        tool_name="insurance_product_query",
        transport_type="http",
        url="http://localhost:18060/mcp",
    )
    
    compliance_tool = MCPTool(
        server="insurance-sales", 
        tool_name="compliance_check",
        transport_type="http",
        url="http://localhost:18060/mcp",
    )
    
    # Get tool definitions for the prompt
    await product_tool.initialize()
    compliance_def = await compliance_tool.to_structured_tool()
    product_def = await product_tool.to_structured_tool()
    
    # Use in LCEL chain
    llm = ChatOpenAI(model="gpt-4o")
    
    # Option A: Direct tool call (no prompt)
    result = await product_tool.ainvoke({
        "product_type": "savings",
        "annual_premium": 100000,
        "term_years": 20
    })
    print("Product query result:", result)
    
    # Option B: Compliance check
    compliance_result = await compliance_tool.ainvoke({
        "text": "这款保险年化收益5%，保本保息！",
        "strict_mode": True
    })
    print("Compliance check:", compliance_result)
    
    await product_tool.close()
    await compliance_tool.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Method 3: TypeScript / Node.js (OpenAI + MCP)

```typescript
/**
 * insurance-sales-mcp — OpenAI Responses API + LangChain JS Integration
 */

import { tools } from "@langchain/mcp-adapters";
import { ChatOpenAI } from "@langchain/openai";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { HumanMessage } from "@langchain/core/messages";

async function main() {
  // Connect via HTTP transport
  const client = await tools.mcp({
    url: "http://localhost:18060/mcp",
    headers: {
      "X-API-Key": process.env.SERVER_API_KEY || "",
    },
  });

  // Get all MCP tools
  const langchainTools = client.tools;
  
  console.log(`Loaded ${langchainTools.length} MCP tools`);
  for (const t of langchainTools) {
    console.log(`  - ${t.name}: ${t.description.substring(0, 60)}...`);
  }

  // Create agent
  const model = new ChatOpenAI({ model: "gpt-4o" });
  const agent = await createReactAgent({
    llm: model,
    tools: langchainTools,
  });

  // Test query
  const result = await agent.invoke({
    messages: [new HumanMessage("查询香港重疾险产品，预算每年5万")],
  });

  console.log("\nAgent output:", result.messages[result.messages.length - 1].content);
  
  client.close();
}

main().catch(console.error);
```

---

## Method 4: OpenAI Agents SDK (Native MCP)

```python
"""
insurance-sales-mcp — OpenAI Agents SDK + MCPServerSse integration
Alternative: use MCPServerStdio for local deployment
"""

from openai import OpenAI
import asyncio

async def main():
    client = OpenAI()
    
    # Use our MCP server as a remote tool in Responses API
    response = await client.responses.create(
        model="gpt-5.5",
        tools=[
            {
                "type": "mcp",
                "server_name": "insurance-sales",
                "url": "http://localhost:18060/mcp",
                # "authorization": "Bearer ${SERVER_API_KEY}",  # for auth
            },
        ],
        input="查询香港储蓄险产品，年缴10万港元"
    )
    
    print(response.output_text)

asyncio.run(main())
```

---

## Security Notes

1. **API Key**: Always use `SERVER_API_KEY` — never hardcode in source code
2. **CORS**: Configure `CORS_WHITELIST` to restrict allowed origins
3. **Rate Limiting**: Our server_http_r27_auth.py enforces 60 req/min per IP
4. **HTTPS Required**: For production, always use HTTPS (OpenAI requires it for remote MCP)
5. **PII Masking**: All PII is masked before external transmission

---

## Testing Checklist

- [ ] Install `langchain-mcp-adapters` + `langgraph`
- [ ] Start `server_http_r27_auth.py` with test API key
- [ ] Run Method 1 (LangGraph) — verify all 5 tools loaded
- [ ] Run Method 2 (LCEL) — verify individual tool calls work
- [ ] Test compliance_check BLOCKED case → verify RL rules trigger
- [ ] Test insurance_product_query → verify product database returns
- [ ] Test needs_assessment → verify client grading works
- [ ] Cleanup: `await client.close()` / `await mcp_client.close()`

---

## References

- LangChain MCP Adapters PyPI: https://pypi.org/project/langchain-mcp-adapters/
- LangChain MCP Docs: https://docs.langchain.com/oss/python/langchain/mcp
- LangGraph Prebuilt Agents: https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/
- OpenAI Responses API + MCP: https://developers.openai.com/api/docs/guides/tools-connectors-mcp
