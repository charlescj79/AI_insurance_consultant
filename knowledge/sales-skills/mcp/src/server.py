#!/usr/bin/env python3
"""
保险咨询销售 MCP Server — stdio模式入口 (R32 模块化重构)
==========================================================
协议: Model Context Protocol (JSON-RPC over stdio)
版本: 1.3.0 (v2.0 + P1.1 模块化 + GL34工具)

用法:
  python -m src.server              # stdio MCP server
  python src/server.py              # 直接运行（兼容旧路径）

工具列表 (11 tools v3.0):
  1. insurance_product_query         - 产品条款查询
  2. compliance_check               - 合规检测（红线+黄线+GL-44）
  3. needs_assessment               - 客户需求诊断
  4. objection_handler              - 异议处理话术生成
  5. private_sop_runner             - 私域SOP执行器
  6. compliance_rewrite             - 违规内容自动改写
  7. lifecycle_analyzer             - 客户生命周期分析
  8. client_crm_tag                 - CRM标签同步与分级管理
  9. multi_turn_dialogue            - 多轮对话上下文管理器
 10. compliance_trend_analysis      - 合规趋势分析
 11. gl34_compliance_check          - GL34分红保单治理检查（新增）
"""
import sys, json, os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.compliance_check import (RED_LINE_RULES, YELLOW_LINE_RULES,
    scan_rules as _scan_rules)

MCP_TOOLS = [
    {"name": "insurance_product_query", "description": "查询香港保险产品条款摘要，含保障范围/免责条款/合规要点",
     "inputSchema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["list", "detail"]}, "product_name": {"type": "string"}}, "required": ["action"]}},
    {"name": "compliance_check", "description": "14条红线+4条黄线自动化合规扫描（GL-44/GN16），返回BLOCKED/FLAGGED/PASS",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}, "strict_mode": {"type": "boolean"}}, "required": ["text"]}},
    {"name": "needs_assessment", "description": "客户需求诊断：提取风险信号、客户分级(A/B/C/D)、紧迫度(urgent/warm/cold)",
     "inputSchema": {"type": "object", "properties": {"message": {"type": "string"}, "context_history": {"type": "array"}}, "required": ["message"]}},
    {"name": "objection_handler", "description": "6大类异议场景+3层级话术(light/medium/heavy)生成",
     "inputSchema": {"type": "object", "properties": {"category": {"type": "string", "enum": ["price","trust","delay","compare","credibility","scope"]}, "scenario": {"type": "string"}, "tier": {"type": "string", "enum": ["light","medium","heavy"]}}}},
    {"name": "private_sop_runner", "description": "Day-0至Day-7私域客户跟进SOP（含触达时机/话术模板/合规规则）",
     "inputSchema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["day-sequence","customer-journey","get-schedule"]}, "day": {"type": "integer"}, "grade": {"type": "string"}}, "required": ["action"]}},
    {"name": "compliance_rewrite", "description": "违规内容自动合规修复，返回改写前后对比+改动说明+二次验证结果",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}, "target_rules": {"type": "array"}}, "required": ["text"]}},
    {"name": "lifecycle_analyzer", "description": "D0→D30客户生命周期分析：认知/信任/方案/决策/转化5阶段模型+优化策略",
     "inputSchema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["analyze","get_stages","optimize"]}, "last_touch_day": {"type": "integer"}, "customer_grade": {"type": "string"}}}},
    {"name": "client_crm_tag", "description": "CRM多维度标签生成(风险/意向/合规/生命周期)及查询导出",
     "inputSchema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["generate","query","export_all","categorize_tags"]}, "session_id": {"type": "string"}, "customer_grade": {"type": "string"}}}},
    {"name": "multi_turn_dialogue", "description": "stdio多轮对话上下文管理（80轮滑动窗口）",
     "inputSchema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["create","add_turn","get_context","summarize","list_sessions","delete"]}, "session_id": {"type": "string"}, "content": {"type": "string"}}}},
    {"name": "compliance_trend_analysis", "description": "合规历史趋势分析：高频违规词检测+风险等级评估+改进建议",
      "inputSchema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["analyze","record","get_rule_stats"]}, "session_id": {"type": "string"}}}},
    {"name": "gl34_compliance_check", "description": "GL34分红保单治理合规检查（2026-03-31生效）：PBC管治、基金隔离、盈余分配公平性、GN16利益区分、理赔率准确性、演示利率上限六项规则并行验证",
      "inputSchema": {"type": "object", "properties": {"content": {"type": "string", "description": "保险内容文本"}, "check_type": {"type": "string", "enum": ["all", "pbc_structure", "fund_isolation", "surplus_distribution", "disclosure_quality", "claim_ratio_accuracy", "illustration_rate"], "description": "检查类型"}, "policy_type": {"type": "string", "enum": ["participating", "savings", "critical_illness", "life"], "description": "保单类型"}}, "required": ["content"]}},
]

TOOL_HANDLERS = {}

def _lazy_import(handler_name, module_name):
    """Deferred import to avoid circular dependencies"""
    def wrapper(params):
        mod = __import__(f"tools.{module_name}", fromlist=[handler_name])
        handler = getattr(mod, handler_name)
        return handler(params)
    return wrapper

# Map: MCP tool name → (function name in module, module name)
_TOOLS_MAPPING = [
    ("insurance_product_query", "handle_product_query", "product_query"),
    ("compliance_check", "handle_compliance_check", "compliance_check"),
    ("needs_assessment", "handle_needs_assessment", "needs_assessment"),
    ("objection_handler", "handle_objection_handler", "objection_handler"),
    ("private_sop_runner", "handle_private_sop_runner", "private_sop_runner"),
    ("compliance_rewrite", "handle_compliance_rewrite", "compliance_rewrite"),
    ("lifecycle_analyzer", "handle_lifecycle_analyzer", "lifecycle_analyzer"),
    ("client_crm_tag", "handle_client_crm_tag", "client_crm_tag"),
    ("multi_turn_dialogue", "handle_multi_turn_dialogue", "client_crm_tag"),  # Tool 9 lives in client_crm_tag module
    ("compliance_trend_analysis", "handle_compliance_trend_analysis", "compliance_trend_analysis"),
    ("gl34_compliance_check", "handle_gl34_compliance_check", "gl34_compliance_check"),
]

for _tool_name, _fn_name, _mod_name in _TOOLS_MAPPING:
    TOOL_HANDLERS[_tool_name] = _lazy_import(_fn_name, _mod_name)

def main_stdio_loop():
    """stdio-based MCP server loop (R32: 仅 ~80行)"""
    for line in sys.stdin:
        try:
            msg = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

        method = msg.get("method", "")
        if method == "initialize":
            resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                    "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                               "serverInfo": {"name": "insurance-sales-mcp", "version": "1.3.0"}}}
            sys.stdout.write(json.dumps(resp, ensure_ascii=False, separators=(',', ':')) + "\n")
            sys.stdout.flush()
            continue

        if method == "notifications/initialized":
            continue

        if method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"tools": MCP_TOOLS}}
            sys.stdout.write(json.dumps(resp, ensure_ascii=False, separators=(',', ':')) + "\n")
            sys.stdout.flush()
            continue

        if method == "tools/call":
            params_obj = msg.get("params", {})
            tool_name = params_obj.get("name", "")
            args = params_obj.get("arguments", {})
            handler = TOOL_HANDLERS.get(tool_name)

            if not handler:
                resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
            else:
                try:
                    result = handler(args)
                    resp = {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}
                except Exception as e:
                    resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                            "error": {"code": -32603, "message": str(e)}}

            sys.stdout.write(json.dumps(resp, ensure_ascii=False, separators=(',', ':')) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main_stdio_loop()
