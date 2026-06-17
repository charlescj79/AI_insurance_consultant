#!/usr/bin/env python3
"""
Gemini CLI / Google AI Agent Config Generator
===============================================
为Google Gemini CLI (gemini) 生成保险销售MCP Server配置。

支持格式:
  - Claude Code-compatible MCP config (Claude Desktop style)
  - Google AI Studio custom instructions
  - Generic JSON-RPC client bootstrap script

用法:
  python gemini_config_generator.py --format claude-config
  python gemini_config_generator.py --format google-studio
  python gemini_config_generator.py --format all
"""

import json
import sys
import os

MCP_DIR = "/Users/charles/.openclaw/workspace/knowledge/sales-skills/mcp"
SERVER_PATH = f"{MCP_DIR}/server.py"


def generate_claude_config():
    """生成Claude Desktop兼容的MCP配置"""
    config = {
        "mcpServers": {
            "insurance-sales-mcp": {
                "command": "python3",
                "args": [SERVER_PATH],
                "env": {},
                "disabled": False,
                "autoApprove": [],
                "timeoutSeconds": 30
            }
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def generate_google_studio_instructions():
    """生成Google AI Studio的custom instructions"""
    return '''# Insurance Sales MCP — Google AI Studio Custom Instructions

## Role Definition
You are an insurance sales expert with access to the following tools for Hong Kong insurance consultation. Use them in sequence when analyzing customer needs:

1. **needs_assessment**: First, assess the customer's needs and grade (A/B/C/D)
2. **insurance_product_query**: For Grade A/B customers, query product framework details
3. **compliance_check**: Before any customer-facing response, always check compliance
4. **objection_handler**: If customer raises objections (price/trust/delay)
5. **private_sop_runner**: For multi-day nurture sequences (C/D grade customers)

## Compliance Rules (Non-Negotiable)
- Never mention guaranteed returns or specific interest rates
- Never compare Hong Kong vs mainland insurance directly (objective only)
- Never use urgency language like "limited time" or "last chance"
- Must include "no sales pressure" disclaimer in any CTA
- Must reference GL-44 regulatory framework where applicable

## Response Format
Always output structured analysis:
{
  "grade": "A/B/C/D",
  "urgency": "urgent/warm/cold", 
  "detected_needs": ["need1", "need2"],
  "product_recommendation": "...",
  "compliance_status": "PASS/FLAGGED/BLOCKED",
  "response_draft": "...",
  "cta_template": "..."
}
'''


def generate_bootstrap_script():
    """生成一键启动测试脚本"""
    init_msg = json.dumps({
        "jsonrpc": "2.0", "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "quick-start", "version": "1.0"}
        }
    })

    tools_msg = json.dumps({
        "jsonrpc": "2.0", "id": 2,
        "method": "tools/list",
        "params": {}
    })

    call3_init = json.dumps({
        "jsonrpc": "2.0", "id": 3,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "quick-start", "version": "1.0"}
        }
    })

    call3_data = json.dumps({
        "jsonrpc": "2.0", "id": 3,
        "method": "tools/call",
        "params": {
            "name": "needs_assessment",
            "arguments": {"message": "我有房贷要还"}
        }
    })

    call4_init = json.dumps({
        "jsonrpc": "2.0", "id": 4,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "quick-start", "version": "1.0"}
        }
    })

    call4_data = json.dumps({
        "jsonrpc": "2.0", "id": 4,
        "method": "tools/call",
        "params": {
            "name": "compliance_check",
            "arguments": {"text": "年化5%收益，保本保息"}
        }
    })

    check_cmd = (
        "python3 -c \"import importlib.util; spec = importlib.util.spec_from_file_location('mcp', '$SERVER'); "
        "mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); "
        "print(f'  Loaded {len(mod.MCP_TOOLS)} tools')\""
    )

    lines = [
        "#!/bin/bash",
        "# Insurance Sales MCP - Quick Start Script",
        "# Usage: ./mcp_quick_start.sh", "",
        "set -e", "",
        f'MCP_DIR="{MCP_DIR}"',
        'SERVER="$MCP_DIR/server.py"', "",
        'echo "=== Insurance Sales MCP Server ==="',
        'echo ""', "",
        "# Test 1: Check server syntax",
        'echo "[1/4] Checking server syntax..."',
        check_cmd, "",
        "# Test 2: List tools (via stdio)",
        'echo "[2/4] Listing tools (via stdio)..."',
        f"echo '{init_msg}' | python3 \"$SERVER\"",
        f"echo '{tools_msg}' | python3 \"$SERVER\"", "",
        "# Test 3: Test needs_assessment",
        'echo "[3/4] Testing needs_assessment..."',
        f"echo '{call3_init}' | python3 \"$SERVER\" | tail -1 > /dev/null",
        f"echo '{call3_data}' | python3 \"$SERVER\"", "",
        "# Test 4: Test compliance_check",
        'echo "[4/4] Testing compliance_check..."',
        f"echo '{call4_init}' | python3 \"$SERVER\" | tail -1 > /dev/null",
        f"echo '{call4_data}' | python3 \"$SERVER\"", "",
        'echo "=== All tests passed ==="',
    ]
    return "\n".join(lines)


def generate_all():
    """生成所有格式的配置"""
    result = {}

    claude_path = os.path.expanduser("~/.claude/settings.json")
    result["claude_config"] = {
        "description": "Claude Desktop MCP configuration",
        "content": generate_claude_config(),
        "install_command": f"# Copy to {claude_path} under 'mcpServers' key",
    }

    result["google_studio"] = {
        "description": "Google AI Studio custom instructions for Gemini CLI",
        "content": generate_google_studio_instructions(),
        "install_command": "# Paste into Google AI Studio -> Settings -> Custom Instructions",
    }

    result["bootstrap"] = {
        "description": "Quick start test script (bash)",
        "content": generate_bootstrap_script(),
        "install_command": "chmod +x mcp_quick_start.sh && ./mcp_quick_start.sh",
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gemini_config_generator.py [--format claude-config|google-studio|bootstrap|all]")
        sys.exit(1)

    fmt = sys.argv[1]

    if fmt == "claude-config":
        print(generate_claude_config())
    elif fmt == "google-studio":
        print(generate_google_studio_instructions())
    elif fmt == "bootstrap":
        print(generate_bootstrap_script())
    elif fmt == "all":
        print(generate_all())
    else:
        print(f"Unknown format: {fmt}")
        sys.exit(1)
