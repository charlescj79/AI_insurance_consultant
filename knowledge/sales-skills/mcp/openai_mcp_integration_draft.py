#!/usr/bin/env python3
"""
insurance-sales-mcp — OpenAI Responses API + MCP Integration Draft (R31)

This script demonstrates how to connect our 10-tool MCP Server 
to OpenAI's platform via multiple integration paths.

Integration Paths:
  A) Direct OpenAI Responses API (type: "mcp") — recommended
  B) langchain-mcp-adapters bridge → OpenAI model
  C) LangChain/LangGraph agent with MCP tools
  
Compliance Notes:
  - All PII auto-masking in compliance_check tool
  - RL-010 cross-border restrictions built-in
  - Session TTL data purging prevents retention violations
"""

# ============================================================
# Path A: Direct OpenAI Responses API with remote MCP server
# ============================================================

def openai_responses_mcp_integration():
    """
    Integration via OpenAI Responses API's native MCP support.
    
    Our server_http.py serves MCP-compliant HTTP endpoints.
    OpenAI can connect directly via: tools[].type: "mcp"
    
    Requirements:
    1. Public HTTPS endpoint for our MCP server
    2. (Optional) OAuth/Bearer token auth
    3. MCP server must implement list_tools + call_tool
    
    Code Reference:
    https://developers.openai.com/api/docs/guides/tools-connectors-mcp
    """
    return """
# Example: OpenAI Responses API with our insurance MCP server

import httpx

def list_mcp_tools(server_url: str) -> list[dict]:
    '''Discover tools from remote MCP server'''
    resp = httpx.post(
        f"{server_url}/v1/tools/list",
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}
    )
    tools = []
    for tool in resp.json()["result"]["tools"]:
        tools.append({
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"]
        })
    return tools

def call_tool(server_url: str, tool_name: str, arguments: dict) -> str:
    '''Invoke a specific MCP tool'''
    resp = httpx.post(
        f"{server_url}/v1/tools/{tool_name}/call",
        json={"jsonrpc": "2.0", "method": "tools/call", 
              "params": {"name": tool_name, "arguments": arguments},
              "id": 1}
    )
    return resp.json()["result"]["content"]

# Usage with OpenAI SDK
from openai import OpenAI

client = OpenAI()
server_url = "https://your-mcp-server.example.com/mcp"

# 1. Discover tools (auto-discovery)
tools = list_mcp_tools(server_url)

# 2. Send to OpenAI — model decides when to call each tool
response = client.responses.create(
    model="gpt-5.5",
    tools=[
        {
            "type": "mcp",
            "server_label": "insurance-sales",
            "server_description": "HK Insurance Sales Advisory MCP Server — GL-44 & RL-010 Compliant",
            "server_url": server_url,
            "require_approval": "never"  # or "always" for safety audit mode
        }
    ],
    input=[
        {"role": "user", 
         "content": "Compare term life plans for a 35-year-old non-smoker in HK"}
    ]
)

# 3. Model automatically calls compliance_check, needs_scoring, etc.
print(response.output)
"""


# ============================================================
# Path B: LangChain MCP Adapters Bridge
# ============================================================

def langchain_mcp_bridge():
    """
    Use langchain-mcp-adapters to convert our MCP tools into 
    LangChain-compatible tool definitions, then use with OpenAI model.
    
    Supports multi-server scenarios (e.g., combine insurance MCP + web search).
    """
    return """
# Integration via langchain-mcp-adapters → OpenAI agent

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

async def build_insurance_agent():
    # 1. Connect to our MCP server
    client = MultiServerMCPClient({
        "insurance-sales": {
            "transport": "http",
            "url": "https://your-mcp-server.example.com/mcp",
            # Optional auth:
            # "headers": {"Authorization": "Bearer YOUR_API_KEY"},
        },
        # Example: also connect web search MCP for real-time data
        "web-search": {
            "transport": "http",
            "url": "https://websearch-mcp.example.com/mcp",
        }
    })
    
    # 2. Get LangChain-compatible tools (auto-converted from MCP)
    tools = await client.get_tools()
    
    # 3. Build agent with OpenAI model
    llm = ChatOpenAI(model="gpt-5.5")
    agent = create_react_agent(llm, tools)
    
    return agent

# Usage
agent = asyncio.run(build_insurance_agent())
result = agent.invoke({
    "messages": [
        ("user", "What insurance product meets these needs: age 40, family of 3, budget HK$10k/month")
    ]
})
"""


# ============================================================
# Path C: LangGraph direct MCP (no OpenAI dependency)
# ============================================================

def langgraph_direct_mcp():
    """
    Pure LangGraph agent with our MCP tools — no model lock-in.
    Works with any model that supports function calling.
    """
    return """
# LangGraph direct MCP integration

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async def build_graph_agent():
    client = MultiServerMCPClient({
        "insurance-sales": {
            "transport": "http", 
            "url": "https://your-mcp-server.example.com/mcp"
        }
    })
    
    tools = await client.get_tools()
    
    # Model-agnostic: swap models freely
    agent = create_react_agent("claude-sonnet-4-6", tools)
    return agent
"""


# ============================================================
# Path D: Secure MCP Tunnel (for private/nested servers)
# ============================================================

def secure_mcp_tunnel_integration():
    """
    For servers behind NAT/firewall, use OpenAI's Secure MCP Tunnel.
    
    Download tunnel client from: https://github.com/openai/tunnel-client
    """
    return """
# Option: Use OpenAI's Secure MCP Tunnel for private deployments

# 1. Install tunnel client (download from openai/tunnel-client releases)
# pip install openai-tunnel-client  # (when available)

# 2. Run tunnel in parallel with your MCP server
tunnel --server-url http://localhost:18060/mcp \\
       --output-format json | tee tunnel_output.json

# 3. Use the returned secure URL in OpenAI Responses API
# {
#   "type": "mcp",
#   "server_url": "https://<tunnel-id>.openai.app/mcp",
#   "require_approval": "never"
# }
"""


# ============================================================
# Compliance Checklist for Platform Integration
# ============================================================

def compliance_checklist():
    """
    Required compliance items before any platform deployment.
    """
    return [
        # PII & Data Protection
        {"id": "PII-01", "status": "DONE", "item": "PII auto-masking in compliance_check tool"},
        {"id": "PII-02", "status": "DONE", "item": "Session TTL expiry with automatic data purge"},
        
        # GL-44 Compliance
        {"id": "GL44-01", "status": "DONE", "item": "RL-002: 收益承诺禁则 in compliance_check"},
        {"id": "GL44-02", "status": "DONE", "item": "YL-001/003/005: 演示利率标注"},
        {"id": "GL44-03", "status": "DONE", "item": "Product query always marks non-guaranteed returns"},
        
        # RL-010 Cross-border Red Line
        {"id": "RL010-01", "status": "DONE", "item": "7 red-line checks for cross-border sales text"},
        {"id": "RL010-02", "status": "REQUIRES_ADD", "item": "Mandatory disclaimer in all platform READMEs"},
        
        # Platform-specific
        {"id": "PLAT-01", "status": "PENDING", "item": "OpenAI: Add Bearer token auth layer"},
        {"id": "PLAT-02", "status": "PENDING", "item": "GitHub: Confirm Apache-2.0 LICENSE file"},
        {"id": "PLAT-03", "status": "PENDING", "item": "All platforms: Add regulatory disclaimer"},
    ]


if __name__ == "__main__":
    print("=== insurance-sales-mcp: OpenAI Integration Draft (R31) ===\n")
    
    paths = [
        ("Path A — Direct OpenAI Responses API MCP", openai_responses_mcp_integration),
        ("Path B — LangChain MCP Adapters Bridge", langchain_mcp_bridge),
        ("Path C — LangGraph Direct MCP", langgraph_direct_mcp),
        ("Path D — Secure MCP Tunnel", secure_mcp_tunnel_integration),
    ]
    
    for name, fn in paths:
        print(f"\n{'='*60}")
        print(f"{name}")
        print(f"{'='*60}")
        print(fn())
    
    print(f"\n{'='*60}")
    print("Compliance Checklist")
    print(f"{'='*60}")
    for item in compliance_checklist():
        status_icon = "✅" if item["status"] == "DONE" else "🔴" if item["status"] == "REQUIRES_ADD" else "⏳"
        print(f"  {status_icon} [{item['id']}] {item['item']}")
