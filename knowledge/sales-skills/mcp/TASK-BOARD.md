# TASK-BOARD.md — MCP Product Development Queue

## 当前状态 (R34 2026-06-17)
- 总任务: 8
- 已完成: **10** (R36新增 GL34合规工具v2代码实现+MCP Server v3.0全量验证) (R31+R32新增：SKILL.md, LangChain集成草案, GN16调研, 分发策略)
- 进行中: 1 (P4.1 PyPI包构建准备)
- 阻塞: 1 (Docker Desktop / GitHub repo — 待CJ操作)

## P0 — 工程化重构（Phase 1）

- [x] **P1.1** ✅ 拆分 `server.py`(1457行) → `src/` 模块化目录结构
  - 10个独立工具文件（每个 <150行，最长143行）
  - stdio入口 128行，HTTP transport 107行
  - 1061行总代码 vs 原3470行 → **-69%** (去重+清理)
  - ✅ 冒烟测试 10/10 通过

- [ ] **P1.2** HTTP transport (src/server_http.py) 已完成 ✅
  - ⚠️ TODO: 添加 API key auth 中间件（安全红线，R31高优事项）

- [x] **P1.3** CLI 模块分离 → `src/cli/` ✅（已存在 cli/ 目录，结构独立无冲突）

- [x] **P1.4** `.agents.md` ✅ + `specs/mcp-tools.json` ✅
  - .agents.md ✅ 创建完成（含架构地图+Edit规则+Task Flow）
  - specs/mcp-tools.json ✅ 10个工具的JSON Schema

- [ ] **P1.5** 创建 `tests/unit/test_tools/` + 每个工具至少3条测试用例

## P1 — CLI + Agentic 升级（Phase 2）

- [ ] **P2.1** CLI 添加 `mcp-call` subcommand → 直接调用 MCP tools
- [ ] **P2.2** Agentic workflow state machine (src/lifecycle/state_machine.py)
- [ ] **P2.3** Session memory store (src/lifecycle/memory_store.py)

## P2 — OpenClaw Harness（Phase 3）

- [ ] **P3.1** Cron payload 重写：读取 TASK-BOARD.md → 完成下一项
- [ ] **P3.2** Subagent 模式 + git commit 自动化
- [ ] **P3.3** CI pipeline (test_all.sh)

## P3 — MCP Server 发布（Phase 4）

### R32新增：外部平台分发策略已就绪 ✅

- [x] **P4.0** ✅ Glama.ai registry提交方案完成 (R32报告)
- [x] **P4.1** ✅ Smithery.ai catalog提交路径确定 (`npm install -g @smithery/cli`)
- [x] **P4.2** ✅ Official MCP Registry API v0.1 提交流程确认
- [x] **P4.3** ✅ PulseMCP人工审核目录提交准备
- [x] **P4.4** ✅ Agensi.io SKILL.md生成完成 + 8点安全扫描预期通过
- [ ] **P4.5** PyPI package (`insurance-mcp`) + `uvx` 安装支持
- [ ] **P4.6** Docker image 构建 (含 API key auth)
- [ ] **P4.7** Smithery托管部署

## 🔴 阻塞项（需CJ操作）
1. GitHub repo URL → git push + CI → 官方Registry/Glama/Smithery提交前置条件
2. Docker Desktop 安装 → 验证容器化部署和n8n端到端测试
3. PyPI account credentials → `twine upload`
4. HTTPS域名+证书 → OpenAI remote MCP要求HTTPS
5. MCP Registry API key → registry.modelcontextprotocol.io token
6. SERVER_API_KEY种子值 → 安全初始化

## R34新增：外部平台对接（Phase 5）
- [x] **P5.1** ✅ Discord Bot MVP (`discord_bot_mvp.py`) — slash commands自动生成 + 合规声明
- [ ] **P5.2** Slack Bolt integration (企业版延伸)
- [x] **P5.3** ✅ Gemini CLI / Antigravity 2.0 MCP配置方案
- [ ] **P5.4** Flowise低代码集成文档
[-] **P5.5** ❌ WeChat Mini Program → 降级P4(跨境合规风险)
