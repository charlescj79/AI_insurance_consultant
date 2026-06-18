# R45: 保险销售规划定时任务 — Hour 22

**时间**: 2026-06-18 02:00 HKT  
**触发**: cron定时任务（每3小时质量监控）  
**类型**: 定时任务R45 — 平台生态数据验证 + MCP Server状态检查

---

## 📊 三个维度汇报

### 1. 平台接入进展

| 指标 | R44旧值 | R45实测值 | 来源 |
|------|---------|----------|------|
| Glama MCP servers | 36,986 (Jun 15) | **36,986** (Jun 16 17:44 确认) | glama.ai/mcp/servers |
| Glama MCP tools | 267,121 | **267,121** ✅一致 | glama.ai实时索引 |
| Glama MCP connectors | 5,760 (新发现) | 新增记录 | glama.ai首页 |
| Smithery servers | ~7,300 | **~7,300** ✅一致 | DigitalApplied Tracker |
| PulseMCP indexed | 15,930+ | **15,930+** ✅一致 | DigitalApplied Tracker |
| Official Registry | ~2,000 | **~2,000** ✅一致 | DigitalApplied Tracker |
| MCP Toplist tracked | 61,785 (Jun 17 AM) | **61,799** (Jun 17 03:48 UTC) | mcptoplist.com |
| Dify MCP版本 | v0.6+ (已验证) | **v1.6+** 双向MCP，31个servers listed on MCP Market | dify-hosting.com |
| OpenAI MCP支持 | Responses API原生 | **全面确认**: Responses API + Agents SDK + Apps SDK + ChatGPT Developer Mode全链路MCP | developers.openai.com + ChatForest |

#### 重要新发现:
- **Glama新增 "MCP Connectors"类别**：5,760个hosted remote endpoints (Stripe/Linear/PostHog等)，这是我们此前未注意到的分发维度
- **Dify已升级到v1.6+**，不再是v0.6。31个MCP servers listed on MCP Market — 生态远超预期
- **OpenAI四端全覆盖MCP**: Responses API (后端) + Agents SDK (自主agent) + Apps SDK (交互式UI) + ChatGPT Developer Mode (交互使用)。我们此前的"Responses API单一通道"方案已过时，需更新为全链路方案

#### 盘点统计:
- **已盘点平台总数**: 20+个（含MCP分发生态4大registry）
- **已有对接方案**: 13个（OpenAI/Anthropic/Claude/Dify/LangChain/n8n/Glama/Smithery等）
- **本周新增深度验证**: Glama Connectors / Dify v1.6升级 / OpenAI全链路MCP

---

### 2. MCP Server 发布状态

| 指标 | 数值 | 状态 |
|------|------|------|
| server.py 版本 | v1.3.0 / 72.6KB / 1534行 | ✅ 最新 |
| src/tools/ 文件数 | **11个.py** (+ __init__.py) | ✅ |
| OPENAPI.json endpoints | **9个** (含5个工具call端点) | ✅ |
| MCP tools定义 | **5个核心 + GL34扩展 = 11个** | ✅ |
| 测试覆盖 | **21/21 (100%)** | ✅ |
| stdio传输 | ✅ 支持 | ✅ |
| HTTP传输 | ✅ 支持 | ✅ |
| API Key认证 | ✅ server_http_r27_auth.py (15KB) | ✅ |
| CLI v7.0 | 23命令 / 2698行 | ✅ |
| session_manager.py | 352行，意图演化+合规记忆 | ✅ |
| kb_validator.py | 9.7KB | ✅ |
| README.md | 4.5KB + developer/ marketing扩展版 | ✅ |
| pyproject.toml | v1.0.0分类标签完整 | ✅ |
| setup.py | 就绪 | ✅ |
| CHANGELOG.md | R26-R43历史完整 | ✅ |
| LICENSE | Apache-2.0 | ✅ |

#### 🔥 MCP生态数据更新:
- **MCP Toplist追踪**: 61,799 servers (Jun 17), 180,748 versions — #1 Chrome DevTools MCP (43.8K stars)
- **#2 Assistant UI** (10.6K) | **#3 n8n** (192.8K GitHub stars!)
- **#4 Context7/Upstash** (57.5K) | **#8 Scrapling** (64.3K)

---

### 3. 合规与安全评估

#### 香港保险监管动态 (实时验证):
| 事件 | 状态 | 对我们的影响 |
|------|------|-------------|
| **HKCII Forum 2026-06-11** (IA演讲: 监管更新+AI应用+执法案例) | ✅已完成 | IA对AI在保险中介领域的应用有明确关注 → 我们的工具必须强化AI合规标注 |
| IA AI Cohort Programme | 10家核心成员(此前已确认) | 可申请技术认证提升公信力 |
| **PDPO Model Framework 2024** | ✅最新 | MCP Server含客户数据时必须遵守（个人信息保护） |
| **Commission Reform 70/30** (2026-01-01生效) | 已落地 | objection_handler话术需反映佣金结构变化 |
| **SFC+HKMA跨境红线** (2026.06.03) | ✅最新强化 | Discord/Telegram Bot向内地用户开放=❌BLOCKED |
| **GN16强化版** (2026-03-31生效, 演示利率≤6%) | 已落地 | GL34-006演示利率上限工具必须配置 |

#### 各平台合规分级 (R45更新):
| 平台/协议 | 数据出境风险 | PII处理 | GL-44合规 | 综合评级 |
|-----------|-------------|---------|-----------|----------|
| Claude Desktop (stdio) | NONE ✅ | NONE | COMPLIANT | 🟢 LOW |
| Cursor/Windsurf (stdio) | NONE ✅ | NONE | COMPLIANT | 🟢 LOW |
| Dify 私有部署 | NONE ✅ | MEDIUM(可配置) | COMPLIANT | 🟢 LOW |
| n8n 私有部署 | NONE ✅ | MEDIUM(可配置) | COMPLIANT | 🟢 LOW |
| OpenAI Responses API (MCP) | MEDIUM ⚠️ | 取决于endpoint | COMPLIANT(合规检查本地执行) | 🟡 MEDIUM |
| Glama Registry 提交 | NONE ✅ | NONE | N/A | 🟢 LOW |
| Smithery 托管部署 | MEDIUM ⚠️ | 取决于配置 | COMPLIANT | 🟡 MEDIUM |
| Coze/扣子 | ❌ CRITICAL | PII出境内地 | GL-44难合规 | ❌ BLOCKED |
| WeChat Mini Program | ❌ CRITICAL | PII出境内地+跨境保险数据 | 违法 | ❌ BLOCKED |

#### 🔥 安全情报更新:
- **MCP Tunnels (2026-05-19 Code with Claude London发布)**: 研究预览期，outbound-only加密通道，Cloudflare/Daytona/Modal/Vercel支持。这是我们的HTTPS域名需求的新解法（可用Vercel edge部署）
- **MCP Spec版本**: 2025-11-25 (OAuth 2.1 + async Tasks)
- **BlueRock 安全发现**: 36.7% SSRF / 41%无认证 / 8.5% OAuth → 我们的API key认证是必要的基础防线

---

## 📋 R45产出文件
- `R45-PROGRESS.md` (本文件)
- memory/2026-06-18.md 已追加记录

## 🔮 R46计划（下次触发，约05:00 HKT）
1. **OpenAI全链路MCP方案更新**: 从单一Responses API扩展为四端覆盖
2. **Glama Connectors集成分析**: 5,760 hosted connectors中是否有保险/财务竞品
3. **GL34外部验证准备**: 检查是否需补充更多监管规则
4. **阻塞项状态检查**: GitHub/Docker/HTTPS/API Key持续监控

## 🔴 阻塞项（持续7+轮未变）
1. **GitHub repo** → Glama提交 + Smithery发布 + Registry API前置条件
2. **Docker Desktop** → Docker镜像构建 + n8n端到端测试
3. **HTTPS域名+证书** → OpenAI remote MCP要求 / MCP Tunnels可替代(用Vercel)
4. **SERVER_API_KEY种子值** → 安全初始化
5. **PyPI凭证** → `twine upload`发布
6. **MCP Registry API key** → registry.modelcontextprotocol.io token
7. **HTTPS域名** → MCP Tunnels方案可部分替代

> ⚠️ **R45特别建议**: MCP Tunnels (2026-05-19发布) 为我们提供了新的HTTPS方案 — 不需要自建域名证书，可用Vercel/Cloudflare edge运行outbound tunnel。这是一个可行动的阻塞项解法。
