#!/usr/bin/env python3
"""
OpenAI Function Calling Schema Adapter
=======================================
将MCP Server的5个工具转换为OpenAI function calling格式。

用于: OpenAI Agents SDK, GPT-4/3.5函数调用, 自定义agent框架集成。

用法:
  python openai_schema_adapter.py list                # 列出所有schema
  python openai_schema_adapter.py get <tool_name>      # 获取单个schema
  python openai_schema_adapter.py generate-config       # 生成完整config JSON
  
示例 - OpenAI Agents SDK:
  from openai_agents import Agent, FunctionTool
  from openai_schema_adapter import build_tools
  tools = [FunctionTool(t["name"], t) for t in build_tools()]
"""

import json
import sys
from typing import Dict, Any

def load_mcp_server():
    """加载server.py中的MCP工具定义"""
    import importlib.util
    mcp_dir = "/Users/charles/.openclaw/workspace/knowledge/sales-skills/mcp"
    server_path = f"{mcp_dir}/server.py"
    
    spec = importlib.util.spec_from_file_location("mcp_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    return mod.MCP_TOOLS


def mcp_tool_to_openai_function(mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
    """将MCP tool定义转换为OpenAI function calling格式"""
    name = mcp_tool["name"]
    description = mcp_tool["description"]
    schema = mcp_tool.get("inputSchema", {})
    
    # 转换parameters为OpenAI格式
    properties = {}
    required_params = []
    
    for prop_name, prop_def in schema.get("properties", {}).items():
        params = {
            "type": prop_def.get("type", "string"),
            "description": prop_def.get("description", ""),
        }
        if "enum" in prop_def:
            params["enum"] = prop_def["enum"]
        if "default" in prop_def:
            params["default"] = prop_def["default"]
        
        properties[prop_name] = params
        if prop_name in schema.get("required", []):
            required_params.append(prop_name)
    
    # 如果properties为空，提供默认参数描述
    if not properties and name == "compliance_check":
        properties = {
            "text": {"type": "string", "description": "待检测的完整文本内容"},
            "strict_mode": {"type": "boolean", "description": "是否启用严格模式（额外隐式违规规则）"}
        }
        required_params = ["text"]
    elif not properties:
        # 默认接受参数化调用，提供通用描述
        properties = {
            "params": {"type": "string", "description": "工具的JSON格式参数字符串"}
        }
    
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required_params if required_params else None,
        }
    }


def build_tools() -> list:
    """构建所有OpenAI function calling格式的tools列表"""
    mcp_tools = load_mcp_server()
    return [mcp_tool_to_openai_function(t) for t in mcp_tools]


def list_schemas():
    """列出所有schema名称和简短描述"""
    tools = build_tools()
    print(f"OpenAI Function Calling Schemas ({len(tools)} functions):")
    print("-" * 60)
    for t in tools:
        print(f"  {t['name']}")
        print(f"    {t['description'][:80]}...")
        print()


def get_schema(tool_name: str):
    """获取单个工具的完整schema"""
    tools = build_tools()
    for t in tools:
        if t["name"] == tool_name:
            return json.dumps(t, ensure_ascii=False, indent=2)
    return None


def generate_config():
    """生成OpenAI-compatible config JSON"""
    tools = build_tools()
    
    config = {
        "model": "gpt-4-turbo",
        "tools": [
            {
                "type": "function",
                "function": t
            }
            for t in tools
        ],
        "tool_choice": "auto",
        "metadata": {
            "adapter_version": "v2.1",
            "source": "insurance-sales-mcp v1.0",
            "protocol": "OpenAI Function Calling",
            "generated_at": "2026-06-17"
        }
    }
    
    return json.dumps(config, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: openai_schema_adapter.py [list|get <name>|generate-config]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_schemas()
    elif cmd == "get":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        if not name:
            print("Error: specify tool name")
            sys.exit(1)
        result = get_schema(name)
        if result:
            print(result)
        else:
            print(f"Error: tool '{name}' not found")
            sys.exit(1)
    elif cmd == "generate-config":
        print(generate_config())
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: openai_schema_adapter.py [list|get <name>|generate-config]")
        sys.exit(1)
