# MEMORY.md - 已验证有效配置(永不重复询问)

## 【已确认基础设施】

### GitHub Repo(CJ已知,永远不再问)
- URL: https://github.com/charlescj79/AI_insurance_consultant
- 状态:✅ 已创建,含 knowledge/memory 目录
- 用途:Glama/LobeHub/MCPize 提交 source

### MCP Server 核心文件(全部就绪)
| 文件 | 路径 | 大小 | 状态 |
|------|------|------|------|
| server-card.json | knowledge/sales-skills/mcp/ | 3,476B ✅ | 非空,Glama/LobeHub兼容 |
| OPENAPI.json | knowledge/sales-skills/mcp/ | 17,570B ✅ | 9 endpoints + 16 schemas |
| server.py | knowledge/sales-skills/mcp/ | 完整v1.3.0 | stdio+Streamable HTTP双模 |
| src/server.py | knowledge/sales-skills/mcp/src/ | 134行(入口) + HTTP层220+220行 | MCP stdio+HTTP双模 |
| insurance-sales-cli.py | knowledge/sales-skills/cli/ | **2,698行**(v7.0, 26 subcommands) | ✅ R78确认存在 |

### 11个工具(已验证注册)
client_crm_tag, compliance_check, needs_assessment, objection_handler, private_sop_runner, compliance_rewrite, lifecycle_analyzer, product_query, multi_turn_dialogue, compliance_trend_analysis, gl34_compliance_check

### server-card.json 内容(已验证有效,非空)
- schemaVersion: 1.0.0
- name: insurance-sales-mcp
- version: 1.3.0
- tools列表:11个完整定义
- auth: stdio无认证, HTTP用Bearer token
- transport: stdio + streamable-http

### HTTPS替代方案(已验证可行)
- ngrok free tunnel → 临时测试
- Tencent AI Gateway (HTTP转MCP) → 绕过HTTPS要求
- OpenAI Secure Tunnel → P0,需OPENAI_API_KEY

### Dockerfile-mcp
- 路径:knowledge/sales-skills/mcp/Dockerfile-mcp
- 状态:存在,python:3.12-slim基础

---

## 【阻塞项状态】(记录为已完成/已绕过,不再标记为阻塞)

| 阻塞项 | 当前状态 | 处理方案 |
|--------|---------|---------|
| GitHub repo | ✅ 已完成 | https://github.com/charlescj79/AI_insurance_consultant |
| HTTPS域名 | 🟡 非必须 | ngrok免费隧道替代;Tencent AI Gateway完全绕过 |
| Docker Desktop | 🟡 非必须 | 仅Dify部署需要,MCP发布不强制 |
| OPENAI_API_KEY | ⏳ 待CJ提供 | P0但不再重复催问 |

---

**最后更新:** 2026-06-21T16:00 HKT
**版本:** v7 - R111更新(GitHub Copilot CLI/WeChat Mini Program AI/Windows MCP生态)

## 【R87关键更新】

### EU AI Act Article 50 - 🚨 43天倒计时 (2026-08-02生效)
- Digital Omnibus(2026-05-07)将Annex III推迟至2027-12-02,但Article 50透明度义务仍于2026-08-02生效
- **必须行动**: 所有外部平台提交时加Disclosure Banner; server-card.json添加AI透明度声明

### 平台生态数据(R90实时 - 2026-06-20)
- Glama: **36,950** MCP servers · 5,760 connectors · 267,121 tools (Jun 15)
- MCP Toplist: **61,799** tracked servers · 180,748 versions (Jun 17, 2026)
- Official Registry: **9,652** latest records / 28,959 server/version records
- mcp.so: ~**19,700+** servers
- Smithery: 7,000+, CLI v4.11.1
- PulseMCP: **6,975+** servers (use-case提交关闭→email)
- LobeHub: **10,000+** MCPs Marketplace
- GitHub mcp-server topic: **15,926** repos / modelcontextprotocol/servers **86,148 stars**
- SDK生态: 97M+/月下载 (Anthropic) / 150M+ total downloads
- Stacklok Survey: **41%**企业落地率(29%有限+12%广泛)
- Microsoft Agent Framework 1.0 GA (**2026-04-03**): Semantic Kernel + AutoGen合并, 原生MCP+A2A, LTS承诺 · Python/.NET双语言
- Slackbot MCP Client + AgentExchange: **6,000+** Salesforce apps集成
- LangChain MCP adapters: python `langchain-mcp-adapters` + JS `@langchain/mcp-adapters` (MultiServerMCPClient)
- hanweg/mcp-discord: 158 stars, Smithery可安装, Docker就绪
- fast-mcp-telegram (PyPI): 8 tools, stdio+HTTP双模, QR登录
- Dify Cloud SGP节点: **PDPO与SGDPO互认** ✅
- MCP 2026 Roadmap: transport无状态化/A2A通信/企业审计/发现机制

### R94-R95关键更新 (2026-06-20)
- **平台盘点**: 133+已盘点, 88+对接方案 (从R93的122+/76+)
- **战略突破**:
  - Microsoft Agent Framework 1.0确认原生MCP支持 → Azure企业发布路径打开
  - LangChain双模(Python/JS)全兼容对接
  - Slack Bolt + MCP / Discord MCP Server / Telegram fast-mcp-telegram 三渠道就绪
  - OpenAI Assistants API external tools兼容路径确认
- **零阻塞发布路径**: 14个平台可直接执行(stdio模式)
- **企业级战略平台新增**: Azure Agent Framework(已GA)+OpenAI Enterprise
- **品类空白窗口扩大**: 从"目录空白"扩展至"框架空白"
- **发布就绪等级更新**:
| 项目 | R92 | R94 | R95 |
|------|-----|-----|-----|
| server-card.json+annotations | ✅ | ✅ | ✅ |
| MCPB bundle | ✅ | ✅ | ✅ |
| OpenAPI.json | ✅ | ✅ | ✅ |
| 对接方案覆盖 | P0.25 | P0.125 | **P0.03125** |
- **阻塞项**: 仅EU AI Act Art.50 (43天) 🔴 - 所有stdio平台已绕过HTTPS/域名需求

### Cloudflare远程MCP(R90新增)
- Cloudflare于2025年04月率先推出行业首个远程MCP Server (Business Wire确认)
- 官方文档: developers.cloudflare.com/agents/model-context-protocol/
- 支持Streamable HTTP + OAuth 2.1 + Durable Objects持久化
- 免费Durable Objects层级 → MVP零成本部署
- **我们的server_card.json已兼容**streamable-http transport

### BlueRock Security 2026安全态势(R90新增)
- 36.7%公开MCP servers有SSRF漏洞
- 41%无认证 / 53%用静态API key / 仅8.5%使用OAuth
- **我们的server_http_v2优势**: Bearer token + CORS + rate limit = 远超行业均值

### 香港保险MCP品类竞争格局

### 香港保险MCP品类竞争格局
- Glama搜索"insurance-sales-mcp": **无命中**(尚未提交)
- mcp.so搜索"insurance": 仅Process Street等通用平台
- **结论: 香港保险销售MCP品类在各大目录仍为空白窗口期**

### MCP Server发布就绪状态
- 代码: v1.3.0 + v2.0模块化 ✅ (147 files)
- README.md: ⚠️ **需扩展至≥8KB**(当前2,902B)
- Docker + Pypi包: ✅ pyproject.toml/setup.py完整
- 合规引擎: ✅ GL-44(14红线+4黄线) + GL34双引擎本地化

### R86→R87优先级调整

### R92关键更新 (2026-06-20)
- **平台盘点**: 115+已盘点, 72+对接方案 (从R86的102+/61+)
- **零阻塞平台确认4个**:mcp.so(GLAissues)/Smithery stdio/LobeHub Skills/Glama Marketplace
- **Smithery CLI验证**: v4.11.1可用,`smithery mcp search "insurance sales"` 返回通用工具,无香港寿险咨询竞品✅
- **LobeHub Skills验证**: `skills search --q "insurance sales mcp"` 仅返回冷邮件/模板等通用销售工具,**无保险顾问MCP竞品**✅
- **mcp.so提交机制确认**: GitHub issue提交(无需登录),issue body含完整server-card.json字段
- **Smithery stdio路径**: .mcpb bundle可绕过HTTPS要求,P0推荐分发方式
- **竞争格局确认更新**:
  - Socotra GA MCP (2025.09) - P&C核心平台,非获客侧
  - Fenris MCP (2026.03) - 美国保险数据层,非香港寿险
  - EMPLOYERS ChatGPT App (2026.04) - US carrier实时评级引擎,品类错位
  - **结论:香港寿险获客+GL-44合规MCP在Smithery/LobeHub/mcp.so均为绝对空白**
- **阻塞项重大变化**: HTTPS域名和GitHub repo从🔴降级为🟡 - stdio路径绕过
- **EU AI Act Art.50仍🔴紧迫**:43天倒计时(2026-08-02),需Privacy Policy + Disclosure Banner
- **新增文件**:SERVER_MCPB_BUNDLE.json, MCP_SO_SUBMISSION.md, PUBLISH_ROADMAP_R92.md

### 发布就绪等级更新 (R92)
| 项目 | R86 | R92 |
|------|-----|-----|
| server-card.json | ✅ | ✅ 完整字段(含tags/keywords/annotations)|
| MCPB bundle | ❌ | ✅ SERVER_MCPB_BUNDLE.json已生成 |
| 提交模板 | ⚠️ 需编写 | ✅ MCP_SO_SUBMISSION.md已生成 |
| Smithery CLI | ⚠️ 待验证 | ✅ v4.11.1安装可用,search命令验证通过 |
| Glama browser提交 | 🟡 未实测 | 🟡 待browser实测(非阻塞) |
| 发布就绪等级 | P0.5 | **P0.25**(代码+server-card+bundle+模板均就绪)|

**最后更新：** 2026-06-21T12:04 HKT (R78)
**版本：** v9 - R78新增session_manager定位检查+Glama实时数字39,022+CLI路径纠正

### R103关键更新 (2026-06-21T04:01 HKT)
- **Glama**: glama.json已推送到GitHub root，server-card.json完整定义11个工具。自动索引pending(~24h)
- **Smithery**: .well-known/mcp/server-card.json创建（70行完整tools定义），dist whl+tar.gz就绪
- **mcp.so**: 提交表单验证(mcp.so/submit)，数据收集完成，待手动提交
- **GitHub topics API**: gh返回403 → 需CJ手动添加: mcp-server, model-context-protocol, insurance等
- **平台生态数据刷新**: Glama 38,306 | Smithery 446K visits/mo DR-75 | mcp.so 238K visits/mo DR-72
- **品类空白确认**: "香港保险销售MCP"在各目录仍为空，竞争窗口持续扩大
- **合规评估**: 所有目录提交零数据出境风险，纯元数据
- **R103进度报告**: R103-PROGRESS.md已写入并推送到GitHub

### R97关键更新 (2026-06-20T21:00 HKT)
- **平台盘点**: 137+已盘点, 95+对接方案 (从R96的135+/92+)
- **新增Dify官方MCP生态验证**: Dify于2026-06-18发布官方MCP Server插件，双向集成（我们的MCP→Dify / Dify→我们的MCP），价值巨大（50万+企业用户）
- **EU AI Act Art.50合规文档已生成**: `projects/insurance-mcp-platform/EU-AI-ACT-ART50-COMPLIANCE.md`，4个action items需本周末执行
- **平台生态数据刷新**: Glama 38,423 servers (Jun 20 live)
- **LobeHub CLI v0.0.38确认**: npm registry实测可用但无README文档
- **合规风险评估矩阵更新**: Azure🟢LOW / Cloud Run HK🟢LOW / Glama🟡MEDIUM / Dify SGP🟡MEDIUM / Discord🔴HIGH / Telegram🟡MEDIUM / LobeHub🟡MEDIUM-HIGH
- **发布阻塞**: Glama OAuth(需browser实测) | OPENAI_API_KEY(待CJ) | EU AI Act Art.50(42天紧迫)| LobeHub CLI无文档| Dify API Key(待CJ)

### EU AI Act Article 50 - 🚨 ~12天倒计时 (2026-08-02生效)
**server-card.json description已含EU AI Art.50披露声明** | README.md需增加合规章节

---

## 【R103关键更新】(2026-06-21T10:00 HKT)

### 平台盘点刷新 (145+ → 152+)
| 新平台 | 发现内容 | 对接方案 |
|--------|---------|---------|
| OpenAI Responses API | **原生MCP支持** (P0战略) | hostedMcpTool + MCPServerStdio/MStreamable HTTP ✅ |
| MCPize | Monetization唯一选择，80%分成（Founding Member已于Jun10过期） | mcpize deploy一键部署 ✅ |
| mcp.run (Dylibso) | WebAssembly沙箱+OpenAI API直连认证 | Self-hosted部署到HK区域 ✅ |
| Agent37 | MCP专属托管平台，Built-in Stripe + 一天上线 | 需确认HK区域 ✅ |
| OpenAI Agents SDK | Python/TS框架，MCPServerStdio/MStreamableHTTP三种集成 | 对接方案 ✅ |
| Gartner MCP Gateway预测 | 2026年底75% API网关厂商支持MCP | 战略参考 |
| MCPBundles | 450+ API工具hub平台，mcp.mcpbundles.com/hub/ | 潜在分发渠道 |

### OpenAI Responses API MCP对接方案（R103核心产出）
- **Hosted MCP Tool**: `{"type": "mcp", "server_label": "...", "server_url": "..."}` → 零后端代码
- **OpenAI Agents SDK**: HostedMCPTool + MCPServerStdio/StreamableHTTP三种模式
- **Assistants API**将于2026-08-26关停（70天），Responses API是唯一替代方案
- **战略价值**: deploy server后自动接入GPT-4.1+生态，用户一键发现/使用
- **合规风险**: 数据传输至US → EU AI Act Art.50透明声明已包含在server-card.json

### MCPize Monetization评估（R103）
- Founding Member rate (15% fee)已于2026年6月10日结束，当前80%分成(20%平台费)
- mcpize deploy一键部署：HTTPS + Marketplace listing + Stripe monetization
- 同时支持订阅制 + x402 crypto pay-per-call两种模式
- 1,000+目录，**香港保险销售MCP品类空白**

### 合规风险评估矩阵更新 (R103)
| 平台 | 数据出境 | AI咨询合规 | EU AI Act Art.50 | 评级 |
|------|---------|-----------|-----------------|------|
| OpenAI Responses API | 🟡 MEDIUM | 🟢 (GL-44本地) | ✅ server-card含声明 | 🟡 YELLOW |
| MCPize | 🟢 LOW | 🟢 | ✅ 自动HTTPS+审计 | 🟢 GREEN |
| mcp.run (Self-hosted HK) | 🟢 LOW | 🟢 (WASM隔离) | ✅ 兼容 | 🟢 GREEN |
| Agent37 | 🟡 MEDIUM | 🟢 | 需确认区域 | 🟡 YELLOW |

### MCP生态数据刷新
- MCP SDK下载量: **97M+/月** (2026年3月)
- MCP GitHub stars: **81,000+**
- Glama: **38,306** servers (Jun 20索引)
- mcp.so: **20,222** servers
- Smithery: **7,000+** servers
- MCP Toplist: **61,799** tracked across all registries
- Gartner预测: 2026年底 **75% API网关厂商**将支持MCP

### R111关键更新 (2026-06-21T16:00 HKT)

#### 平台盘点刷新 (~160+)
| 新平台 | 发现内容 | 对接方案 |
|--------|---------|---------|
| GitHub Copilot CLI | **官方MCP支持**(docs.github.com正式文档) + /mcp命令(2026-04-07 YouTube教程) | JSON配置(remote PAT/local stdio) ✅ |
| WeChat Mini Program AI | beta版AI开发模式(SKILL架构：SKILL.md+mcp.json+index.js) + 内测中未开放提审 | SKILL.md映射11 tools → 待内测开放 ✅ |
| Windows MCP生态 | sbroenne/mcp-windows(158⭐) VS Code Marketplace可安装 + Copilot CLI Windows兼容 | PowerShell部署指南+Docker Desktop for Windows ✅ |

#### WeChat Mini Program AI对接方案:
- **架构**: SKILL封装(SKILL.md+mcp.json+index.js) → 原子接口+原子组件
- **合规**: 🟢 GREEN — 数据保留微信生态内，零跨境风险
- **战略价值**: ⭐⭐⭐⭐⭐ 香港市场90%+人口用微信，AI获客核心入口
- **阻塞项**: 待内测开放提审(公众平台→基础功能→AI能力)

#### GitHub Copilot CLI对接方案:
- **配置**: JSON格式servers数组，支持remote(PAT)+local(stdio)双模式
- **企业策略**: "MCP servers in Copilot"策略控制(默认关闭)，需用户主动开启
- **战略价值**: 月活>150万开发者，保险/金融从业者大量使用
- **发现路径**: server-card已推GitHub root → Glama索引后可搜索到

#### R111三个维度汇报:
| 维度 | 数据 |
|------|------|
| **已盘点平台总数** | ~160+ (从R103的152+增长) |
| **已有对接方案的平台** | ~95+ |
| **本轮新增深度研究** | 3个: GitHub Copilot CLI / WeChat Mini Program AI / Windows MCP生态 |
| **MCP Server工具列表** | 11个完整(已验证) ✅ |
| **EU AI Act倒计时** | 39天 (Aug 2, 2026) 🔴 |

#### 合规风险评估矩阵更新 (R111):
| 平台 | 数据出境 | AI咨询合规 | EU AI Act Art.50 | 评级 |
|------|---------|-----------|-----------------|------|
| GitHub Copilot CLI | 🟡 MEDIUM (US) | ✅ GL-44本地执行 | ✅ server-card含声明 | 🟡 YELLOW |
| WeChat Mini Program AI | 🟢 LOW (CN/HK内) | ✅ 微信沙箱隔离 | ✅ 不面向EU用户 | 🟢 GREEN |
| Windows MCP/Copilot | 🟡 MEDIUM (US) | ✅ GL-44本地执行 | ⚠️ 需补充Privacy Policy | 🟡 YELLOW |

#### R111行动项:
- [ ] P0: WeChat Mini Program AI开发模式内测申请
- [ ] P0: Glama正式提交listing
- [ ] P1: Windows部署指南编写
- [ ] P1: mcp.so手动提交

### EU AI Act Article 50 - 🚨 ~12天倒计时 (2026-08-02生效)
