# Changelog — insurance-sales-mcp

All notable changes to this project will be documented in this file.

## [1.3.0] — 2026-06-18

### Added
- **11 MCP tools** total (up from initial 5)
  - `insurance_product_query` — 香港保险产品查询（list + detail，模糊匹配）
  - `compliance_check` — GL-44/RL-002/RL-010等14条红线+4条黄线合规扫描
  - `needs_assessment` — 客户需求诊断引擎（A/B/C/D分级）
  - `objection_handler` — 6大类×3层级异议处理话术
  - `private_sop_runner` — 私域Day-0~7 SOP全流程执行器
  - `compliance_rewrite` — 违规内容自动改写引擎（前后对比+二次验证）
  - `lifecycle_analyzer` — D0→D30客户生命周期分析（5阶段模型）
  - `client_crm_tag` — CRM标签生成/查询/导出
  - `multi_turn_dialogue` — 80轮会话上下文管理
  - `compliance_trend_analysis` — 历史违规趋势分析+规则统计
  - `gl34_compliance_check` — GL34分红保单治理合规检查（6条规则）
- HTTP transport (FastAPI + uvicorn) on configurable port (default 18060)
- Health endpoint (`/health`, `/v1/tools/list`, `/v1/execute`)
- Session manager with TTL expiration and compliance memory persistence
- Dockerfile-mcp for production deployment
- OpenAI schema adapter (`openai_schema_adapter.py`)
- Gemini CLI config generator (`gemini_config_generator.py`)
- Full OPENAPI.json (9 endpoints + 16 schemas)
- AGENTIC-WORKFLOW-DESIGN.md v2.2
- CHANGELOG (this file)

### Fixed
- Python 3.14 http.server Content-Length truncation bug
- `needs_assessment` grade variable initialization
- Product fuzzy matching (短词匹配：危疾→重疾险)

### Documentation
- Complete README.md with quick start for Claude Desktop, Cursor, Windsurf
- Platform integration guides: Dify, Coze, LangChain, OpenAI Responses API
- Security threat analysis: Tool Poisoning / Shadowing / Rugpull mitigations
- Compliance framework: GL-44 + RL-010 cross-border red lines + GL34
- 强制免责声明模板 for all platforms

### Architecture
- stdio + HTTP dual transport
- JSON-RPC 2.0 base protocol
- Session isolation with auto-cleanup
- Built-in PII stripping pipeline

## [0.1.0] — Initial release
- Core MCP server with 5 tools (product_query, compliance_check, needs_assessment, objection_handler, private_sop_runner)
- Basic stdio transport
- Knowledge base loading from local files
- Compliance rules RL-002 through RL-010
