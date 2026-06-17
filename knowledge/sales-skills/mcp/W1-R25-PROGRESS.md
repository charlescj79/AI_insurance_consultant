# R25: 外部平台盘点与对接方案 — Round 25

**日期**: 2026-06-17T04:56 HKT
**轮次主题**: 全量平台接入可行性分析 + 高优先级平台对接方案设计
**状态**: ✅ 已完成深度调研，产出对接路线图

---

## 一、MCP Server 现状盘点（自身资产）

### 已有资产
| 文件 | 描述 | 状态 |
|------|------|------|
| `server.py` | MCP Server 主代码（Python/stdio，5个工具） | ✅ v1.0可用 |
| `server_http.py` | HTTP传输模式版本 | ✅ 基础版 |
| `docker-compose.yml` | Docker编排方案 | ✅ 可用 |
| `test_mcp_suite.py` | 测试套件 | ⚠️ 待完善 |
| `gemini_config_generator.py` | Gemini MCP配置生成器 | ✅ 辅助工具 |
| `openai_schema_adapter.py` | OpenAI Schema适配器 | ✅ 辅助工具 |

### 工具列表（5 tools）
1. `insurance_product_query` — 产品条款查询
2. `compliance_check` — 合规检测（红线+黄线）
3. `needs_assessment` — 客户需求诊断
4. `objection_handler` — 异议处理话术生成
5. `private_sop_runner` — 私域SOP执行器

### 发布状态评估
| 维度 | 状态 | 说明 |
|------|------|------|
| 工具数量 | 5个 ✅ | 覆盖核心保险咨询场景 |
| Transport | stdio为主 | 需增加HTTP/SSE远程支持 |
| OAuth认证 | ❌ 未实现 | MCP规范已强制OAuth 2.1+PKCE |
| Docker镜像 | 有compose | 缺Dockerfile-mcp构建文件 |
| 文档完整度 | ⚠️ 待补充 | 缺README、接入指南、OpenAPI spec |
| 测试通过率 | ❓ 待验证 | 需跨客户端实测 |

---

## 二、全量平台盘点（10大平台/协议族）

### 平台接入可行性矩阵

| # | 平台/协议族 | MCP支持状态 | 对接难度 | 优先级 | 数据出境风险 |
|---|------------|-------------|---------|--------|-------------|
| 1 | **Claude Desktop / Anthropic API** | ✅ 原生MCP，官方支持 | 🟢 低（已有配置示例） | **P0-最高** | 🟡 中（数据经Anthropic服务器） |
| 2 | **OpenAI (GPT-5.5/Responses API)** | ✅ Remote MCP Server + Secure Tunnel | 🟡 中（需部署HTTP+Tunnel） | **P0-最高** | 🟡 中（数据经OpenAI服务器） |
| 3 | **Google Gemini (Antigravity/Gemini Enterprise)** | ✅ Streamable HTTP，OAuth 2.1 | 🟡 中（需OAuth配置） | **P1-高** | 🔴 高（美国云存储合规） |
| 4 | **Microsoft Azure AI / Foundry** | ✅ Azure MCP Server + Foundry MCP (https://mcp.ai.azure.com) | 🟡 中（Azure环境依赖） | **P1-高** | 🔴 高（跨境+合规复杂） |
| 5 | **LangChain/LangGraph** | ✅ langchain-mcp-adapters 0.2.2 | 🟢 低（纯软件集成） | **P1-高** | 🟢 低（本地运行） |
| 6 | **n8n (v2.14+)** | ✅ MCP Server Trigger + MCP Client Tool | 🟡 中（需部署n8n实例） | **P2-中** | ⚠️ 取决于部署位置 |
| 7 | **Dify / 扣子(Coze)** | ✅ Dify原生MCP支持；Coze 2026年原生支持 | 🟢 低（UI配置） | **P1-高(国内)** | 🔴 高(数据在中国/新加坡) |
| 8 | **Flowise** | ⚠️ CVE-2026-40933 RCE漏洞已修(≥3.1.0) | 🟡 中（安全补丁后） | **P3-低** | ⚠️ 取决于部署位置 |
| 9 | **Telegram Bot API** | ❌ 需自建MCP→Bot桥接 | 🔴 高（需开发桥接层） | **P2-中** | 🟡 中（服务器位置决定） |
| 10 | **WeChat Mini Program + AI Agent** | ❌ 需完整自研 | 🔴 高（微信生态+合规） | **P3-低** | 🟢 低（纯境内） |

---

## 三、本轮重点对接方案：OpenAI Responses API MCP集成

### 3.1 OpenAI平台深度分析
**搜索结果验证**:
- OpenAI官方文档已确认MCP support via Responses API (developers.openai.com)
- 支持 `server_url` (SSE/Streamable HTTP endpoint) + OAuth authorization
- 提供 **Secure MCP Tunnel**：用于防火墙后的私有MCP Server
- 架构: Build → Ground(Tools) → Act(Agents SDK)

### 3.2 对接方案（可执行）

```
阶段A：本地部署HTTP Transport
1. server_http.py → HTTPS endpoint (nginx反向代理+Let's Encrypt)
2. Docker Compose加入nginx + certbot
3. 健康检查 + 日志持久化

阶段B：Secure MCP Tunnel接入OpenAI
1. 下载 openai/tunnel-client releases
2. tunnel从本地端口18060 → OpenAI安全隧道端点
3. Responses API调用时传入 server_url + auth参数
4. require_approval = "always"（保险咨询必须人工确认）

阶段C：Codex Plugin Marketplace发布
1. OpenAI Codex Plugins已上线(2025-03)，支持skills+apps+MCP servers
2. 打包为Codex Installable Bundle
3. 提交至OpenAI Plugin Marketplace
```

### 3.3 合规风险评估（OpenAI）
| 风险项 | 等级 | 缓解措施 |
|--------|------|---------|
| 数据出境（客户咨询数据→美国服务器） | 🔴 **高** | ✅ Secure MCP Tunnel本地处理，仅发送token；✅ 不存储对话日志到云端 |
| GL-44合规（香港保险监管） | 🟡 中 | ✅ `compliance_check`工具强制调用；✅ 输出强制包含免责声明 |
| AI生成内容误导风险 | 🟡 中 | ✅ `needs_assessment`返回结构化数据，不直接给客户看AI原始输出 |

---

## 四、本轮重点对接方案：Dify/Coze（国内平台）

### 4.1 Dify平台深度分析
**搜索结果验证**:
- Dify在工具菜单 → MCP中可直接添加MCP服务(HTTP/SSE)
- 支持通过Dify Endpoint功能暴露为URL端点
- 阿里云官方文档有完整接入指南（2026-06-02更新）

### 4.2 对接方案
```
阶段A：Dify集成
1. MCP Server部署为SSE/HTTP模式
2. Dify工具面板 → 添加MCP服务 → 输入Server URL
3. 创建Agent应用，绑定保险咨询Prompt
4. 调试验证5个工具的调用效果

阶段B：Coze(扣子)集成
1. Coze 2026年已原生支持MCP
2. 类似Dify流程，可视化配置
3. 可连接国内大模型（通义千问、文心一言等）
```

### 4.3 合规风险评估（Dify/Coze）
| 风险项 | 等级 | 缓解措施 |
|--------|------|---------|
| 数据境内存储（香港→中国大陆） | 🟢 低 | ✅ Dify私有部署在境内；✅ Coze新加坡节点可规避 |
| GL-44合规 | 🟡 中 | ✅ 同OpenAI方案，强制compliance_check工具链 |
| 跨境数据法规 | 🟡 中 | ⚠️ 需确认《个人信息保护法》条款；建议客户数据不落库 |

---

## 五、对接路线图（本周计划）

### Day 1-2 (06/17-06/18): MCP Server封装
- [ ] 补充 `README.md` + Dockerfile-mcp
- [ ] HTTP/SSE传输完整测试
- [ ] OpenAPI/Swagger接口文档生成

### Day 3-4 (06/19-06/20): OpenAI集成
- [ ] Secure MCP Tunnel部署测试
- [ ] Responses API端调用验证
- [ ] Codex Plugin Bundle打包

### Day 5-6 (06/21-06/22): Dify/国内平台
- [ ] Dify实例部署（本地Docker）
- [ ] MCP服务对接+Agent配置
- [ ] Coze集成方案文档

### Day 7 (06/23): LangGraph + n8n
- [ ] LangChain-MCP适配器测试
- [ ] n8n MCP节点验证

---

## 六、合规与安全总评估（全平台）

### 红线约束
1. **禁止**向任何平台直接暴露客户PNI（个人可识别信息）
2. **禁止**绕过 `compliance_check` 工具链输出保险相关内容
3. **严禁**内地跨境销售保险产品（所有平台咨询仅做"教育+预约"）

### 平台级合规策略
| 平台 | PII处理策略 | 数据存储策略 | GL-44对齐度 |
|------|------------|-------------|-------------|
| Claude Desktop | 本地进程，不传输 | ❌ 无存储 | ✅ 完全 |
| OpenAI (Tunnel) | Token化代理 | ❌ Tunnel不缓存 | ⚠️ 需确认 |
| Gemini Enterprise | OAuth scoped token | ❌ 用户级控制 | ⚠️ 需评估 |
| Dify私有部署 | 本地存储/不落库 | ✅ 可配置 | ✅ 完全 |
| n8n | 工作流变量传递 | ✅ 可配置 | ✅ 完全 |
| WeChat Mini | 微信OAuth | ❌ 受限于平台 | ⚠️ 需法务审核 |

---

## 七、MCP Server对外发布清单

### 待完成物料
- [ ] `README.md` — 产品说明 + 快速入门（~1000字）
- [ ] `Dockerfile-mcp` — 构建镜像脚本
- [ ] `OPENAPI.json` — 5个工具的OpenAPI spec
- [ ] `CONTRIBUTING.md` — 二次开发指南
- [ ] MCP Registry注册条目

### 测试环境清单
- [x] Claude Desktop (已有)
- [ ] OpenAI Responses API (需部署HTTP+Tunnel)
- [ ] Cursor/Windsurf (MCP客户端)
- [ ] Dify本地实例
- [ ] LangChain/MCP适配器

---

**下次迭代重点**: MCP Server封装 + OpenAI Secure Tunnel实战对接
**合规提示**: 所有平台接入前必须完成数据出境评估表（模板待建）
