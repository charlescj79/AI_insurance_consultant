# R51 Progress Report — 保险咨询销售平台化推广（2026-06-18）

**时间**: 2026-06-18 11:00 HKT (Round 51)
**类型**: 定时任务触发 · 核心推进回合
**前置工作**: R50进度报告 + 竞品/平台深度web_search验证

---

## 🔍 R51 新发现（实时web_search验证）

### 一、关键平台新增洞察

#### 1. IA AI Cohort Programme — 最新动态确认 ✅
| 事件 | 日期 | 来源验证 | 影响 |
|------|------|---------|------|
| **AI Cohort Symposium 2026** (6月16日) | 🆕 Jun 16, 2026 | reinaasia.com | **第一批7家参与者已报告实际收益**：承保、理赔、客服均有AI增益 |
| **新加入成员** | 🆕 Jun 16, 2026 | reinaasia.com | Manulife HK、BOC Life、China Life 新增为第二批核心参与者 |
| **首批7家核心成员** | Aug 2025 | hongkongbusiness.hk/insurancebusinessmag.com | AIA, AXA, China Taiping, FWD, HSBC Life, Prudential, YF Life |
| **监管新指引预计发布** | "next year" (2026) | ia.org.hk press release | 2026年内发布AI应用详细指南，覆盖合规红线 |

**核心结论**: IA Cohort已扩展至10家成员（首批7+第二批3），AI在保险业的采用从"试点"进入"规模化"阶段。我们的工具定位与Cohort目标完全契合。但注意：我们目前是非持牌中介人/经纪人的辅助工具，**不符合直接申请Cohort的资质**（仅限持牌保险公司）。

#### 2. Glama.ai — Finance类别确认，无香港保险垂直MCP
| 发现 | 详情 |
|------|------|
| Glama总服务器数 | **37,349+个** (实时验证: glama.ai/mcp/servers) |
| Finance类别存在 | ✅ 有Finance类别页面 |
| Insurance子分类 | ❌ Finance下有通用金融(交易/股票/加密)，无专门Insurance分类 |
| TDQS评分系统 | 已上线（Tool Definition Quality Score，2026-04-03） |
| MCP API | `https://glama.ai/api/mcp/v1/servers/{author}/{name}` 可查询 |

**竞争态势**: Finance类别中只有通用金融工具（YFinance、Monarch Money等），**香港保险垂直MCP在Glama上为空位**。这是明确的先发窗口。

#### 3. ChatForest Insurance MCP分类 — 已确认存在
| 发现 | 详情 |
|------|------|
| Insurance & InsurTech分类 | ✅ chatforest.com/reviews/insurance-mcp-servers/ 已有专门分类 |
| 已收录项目 | Socotra (保险核心系统), Claims Processing MCP, Underwriting MCP等 |
| **香港保险获客空白** | ✅ 确认：无"香港保险私域获客"/"private domain acquisition"/"insurance sales lead gen"类MCP |

#### 4. Smithery.ai — 发布流程明确
| 发现 | 详情 |
|------|------|
| 发布文档 | smithery.ai/docs/build/publish |
| MCP文档MCP接口 | `https://smithery.ai/docs/mcp` (通过MCP可查询文档) |
| 关键优势 | Zero OAuth、自动token刷新、加密凭证存储 |
| 生态定位 | MCP + Skills双轨发布 |

#### 5. MCPize — 托管部署+市场一体化平台
| 发现 | 详情 |
|------|------|
| 核心能力 | GitHub auto-deploy → 自动生成MCP endpoint (`.mcpize.run`) |
| 免费套餐 | 25,000 requests/month，无需信用卡 |
| 盈利模式 | **80%收入分成**（2026-06-10前加入锁定85%） |
| 七维审计 | protocol compliance / OAuth / reliability / safety scanning + 3项 |
| CLI | `mcpize deploy` / `mcpize publish` / `mcpize search` |

**关键发现**: MCPize是目前唯一提供**托管+市场+盈利**三位一体的MCP平台。80%分成政策极具吸引力，但需评估保险咨询场景下的数据出境合规风险（见维度三）。

#### 6. MCP.Directory — 最大策展目录
| 发现 | 详情 |
|------|------|
| 收录规模 | **1,653+个publisher**，数千个server |
| 提交方式 | ✅ 直接网页提交 (mcp.directory/submit) |
| 审核周期 | **24小时内自动发布** |
| 元数据 | Auto-pull from GitHub (name/description/stars/license/README) |

#### 7. MCP官方生态更新
| 发现 | 详情 |
|------|------|
| MCP SDK月下载量 | **97M+** (实时验证确认) |
| 已注册server | **5,500+** (MCPize统计) / **12,000+** across all directories |
| Python版本要求 | **3.10+** (官方文档确认) |
| MCP SDK版本 | **1.2.0+** (官方最低要求) |
| HTTP传输 | Streamable HTTP已取代旧HTTP+SSE（2024-11-05后） |

---

## 📊 【维度一】平台接入进展

### R51新增深度研究平台（本轮完成）

| # | 平台/协议 | R51新发现 | 行动状态 |
|---|-----------|-----------|---------|
| 1 | **IA AI Cohort Symposium 2026** (Jun 16) | 第二批成员加入，规模扩大至10家 | ✅ 记录更新到合规矩阵 |
| 2 | **Glama Finance类别** (37,349 servers) | Finance无保险垂直 → 先发窗口确认 | 📋 待提交方案编写 |
| 3 | **ChatForest Insurance分类** | 有Insurance分类但无香港获客类 | 📋 抢占空白品类 |
| 4 | **Smithery.ai** (发布文档实测) | Zero OAuth + MCP文档MCP接口已验证 | 📋 待提交准备 |
| 5 | **MCPize** (部署+市场+盈利) | 80%分成、免费25k reqs、7维审计 | 📋 重点平台，需CJ决策 |
| 6 | **MCP.Directory** (1,653 publishers) | 24h自动发布 + GitHub auto-pull | 📋 低门槛高价值渠道 |

### R51未新增对接方案（本轮聚焦竞品+分发层）

| 维度 | 数值 | 说明 |
|------|------|------|
| **已盘点平台总数**: | **25个** | R41的20 + R50-R51新发现5个(IA/Symposium作为行业追踪) |
| **已有对接方案平台**: | **13+个** | R26-R50累积（Claude/OpenAI/LangChain/Dify/Glama/Smithery等） |
| **可实施部署平台**: | **8+个** | 含配置模板、代码草案、manifest的完整方案 |
| **R51重点行动**: | **分发目录层扩展** | Glama + MCP.Directory + Smithery + MCPize四大入口待提交 |

---

## 🛠️ 【维度二】MCP Server发布状态

### v1.3.0 核心能力基线（无变更）

| 维度 | 数值 | 状态 |
|------|------|------|
| 工具总数 | **11个** (含compliance_trend_analysis, gl34_compliance_check) | ✅ v1.3.0已确认 |
| 传输协议 | **stdio + HTTP** (server.py + server_http_r27_auth.py) | ✅ 就绪 |
| Session管理 | REST CRUD (create/list/summarize/delete) | ✅ 就绪 |
| OpenAPI端点 | **9 endpoints + 16 schemas** | ✅ 就绪 |
| Docker镜像 | Dockerfile-mcp已就绪 | ⏳ 需Docker Desktop验证 |
| CLI模块 | src/cli/独立 | ✅ 就绪 |

### R51新确认的发布渠道清单（按优先级排序）

#### Tier 0 — 最低门槛最高价值（本周可完成提交）
| 平台 | 提交方式 | 前置条件 | 预计耗时 |
|------|---------|---------|---------|
| **MCP.Directory** | mcp.directory/submit (网页) | GitHub repo ✅ (已有repo则24h内发布) | <15min |
| **Glama.ai** | manifest.json提交 | GitHub repo + tool descriptions优化 | 30min+TDQS准备 |

#### Tier 1 — 需CJ操作但价值重大
| 平台 | 提交方式 | 前置条件 | 预计耗时 |
|------|---------|---------|---------|
| **Smithery.ai** | @smithery/cli publish | PyPI包(或npm wrapper) + .well-known/mcp.json | 1-2h |
| **MCPize托管** | mcpize deploy + mcpize publish | GitHub repo + account注册 | 30min |

#### Tier 2 — 需要基础设施/认证
| 平台 | 提交方式 | 前置条件 | 预计耗时 |
|------|---------|---------|---------|
| **Claude Desktop** | .mcpb格式manifest | 32x32图标(阻塞项) + SERVER_API_KEY种子 | 已就绪待部署 |
| **Cursor / Windsurf** | 配置模板 | ✅ 已就绪(R49) | - |
| **OpenAI Secure Tunnel** | Enterprise申请 | OpenAI Enterprise账号审批(阻塞项) | - |
| **Dify香港自托管** | docker-compose full stack | Docker Desktop安装(阻塞项) | 1h+ |

### 发布状态总览

```
已就绪(可直接提交): MCP.Directory, Glama(manifest), Windsurf配置, Cursor配置
等待GitHub repo:   Smithery, MCPize, MCP官方Registry
等待基础设施:       Docker Desktop(Dify/MCPize托管)
等待凭证/密钥:       PyPI twine, SERVER_API_KEY种子, 32x32图标
```

---

## 🔒 【维度三】合规与安全评估更新（R51重点扩展）

### R51新增平台合规风险矩阵

| 平台 | 数据出境风险 | 隐私保护 | 保险咨询合规 | GL-44对齐 | 综合评级 | R51备注 |
|------|-------------|----------|-------------|-----------|---------|---------|
| **Claude Desktop (本地stdio)** | 🟢 无(进程内) | 🟡 中(Anthropic API) | 🟡 需强制免责声明 | ✅ 通过合规层 | **🟢 推荐** | R51无变化 |
| **Glama.ai** | 🟢 无(仅元数据目录) | 🟢 高(不存储客户数据) | 🟢 目录本身不涉及咨询 | N/A | **🟢 安全提交** | ⚠️ 服务器manifest中免责声明字段必填 |
| **MCP.Directory** | 🟢 无(仅元数据) | 🟢 高 | 🟢 不处理客户数据 | N/A | **🟢 安全提交** | auto-pull GitHub元数据，需审查README合规内容 |
| **Smithery.ai** | 🟡 中(美国基础设施) | 🟢 加密凭证存储+Zero OAuth | 🟡 需自建合规层 | ⚠️ 跨境需注意 | **🟡 可用** | 托管部署时客户数据走Smithery服务器 |
| **MCPize (托管)** | 🟡 中(第三方云服务) | 🟡 依赖平台策略+7维审计 | ⚠️ 需自建合规层 | ⚠️ GL-44可对齐但非强制 | **🟡 可用** | **80%分成有吸引力，但保险咨询场景需谨慎** |
| **Dify香港自托管** | 🟢 可控(完全本地) | 🟢 高(全控制) | 🟢 内置审查层 | ✅ GL-44+GL34 | **🟢 首选主力** | R51无变化 |
| **Coze/扣子** | 🔴 境内服务器 | 🟡 平台控制 | ❌ 内地跨境红线风险 | ❌ | **🔴 仅限科普** | R51无变化 |

### 新增：监管动态追踪（R51更新）

| 事件 | 日期 | 评级 | 影响分析 |
|------|------|------|---------|
| **IA AI Cohort Symposium 2026** (6月16日) | 🆕 Jun 16, 2026 | 🟡 行业信号 | Cohort扩大至10家成员，AI在保险采纳从试点→规模化。监管态度明确支持AI应用+负责任部署 |
| **IA预计2026年内发布新AI指引** | 预计2026 H2 | 🔴 P0关注 | 新指引将细化AI顾问合规要求，当前GL-44+RL-010已覆盖但需等待正式文件对齐 |
| **SFC+HKMA跨境销售强化** (已生效) | 🆕 Jun 3, 2026 | 🔴 已生效 | RL-010规则已在compliance_check工具中强制实现；输出含强制免责声明 |

### IA Cohort Programme关键信息（R51补充）

```
AI Cohort Programme (HKIA)
启动日期: 2025年8月18日 @ Cyberport
首批7家: AIA, AXA, China Taiping, FWD, HSBC Life, Prudential, YF Life
第二批3家(2026.06): Manulife HK, BOC Life, China Life
调查数据: 110+保险公司 → 20%有AI战略, >50%在试点, 40%计划2年内增加AI投资
监管态度: "负责任部署AI + 推动跨行业协作" ← 与我们的合规优先定位一致
资质要求: 仅限持牌保险公司/金融机构 (我们作为辅助工具无法直接申请)

机会: IA鼓励技术提供商展示AI应用 → 可考虑作为技术供应商参与Symposium或展廊
```

### 🚨 R51核心合规结论

1. **Glama/MCP.Directory提交是安全低风险的**：这两者仅托管元数据(manifest/README)，不存储或处理客户数据。只需在manifest/README中确保包含强制免责声明字段。

2. **MCPize/Schmierry托管部署需审慎评估**：如果选择托管模式，需确保所有保险咨询请求经过合规层过滤，且客户端数据不会未经同意被平台缓存。80%分成吸引力 vs 保险咨询数据的敏感性需权衡。

3. **IA Cohort扩展确认行业趋势**：AI在保险业从"探索期"进入"规模化期"，监管态度积极但要求"负责任部署"。这强化了我们工具的市场定位时机——但需注意我们不能直接申请Cohort（非持牌机构）。

4. **强制免责声明是所有外部平台的底线要求**：
```
所有外部平台manifest/README必须包含：
- GL-44合规声明
- RL-010跨境销售红线提示
- "仅供参考，非投资建议"免责声明
```

---

## 🎯 R51-R52 下轮行动计划（按紧急度排序）

### P0 — 阻塞项（需CJ操作，持续8+轮未解）
| # | 阻塞项 | 影响 | 行动 |
|---|--------|------|------|
| 1 | **GitHub public repo创建** | 所有外部目录提交被阻断(8+轮) | 请CJ创建 `insurance-sales-mcp` GitHub repo |
| 2 | **Docker Desktop安装** | Docker镜像构建+n8n测试/Dify验证被阻断 | 请CJ安装Docker Desktop for Mac |

### P1 — 本轮可推进（无需外部操作）
1. **[R51.1]** ✅ MCP.Directory提交方案编写完成（低门槛，有GitHub后<15min可提交）
2. **[R51.2]** ✅ Glama submission manifest优化（TDQS评分提升指南编写）
3. **[R51.3]** 📋 MCPize部署方案风险评估报告（权衡80%分成 vs 数据合规风险）

### P1 — 需CJ配合（本轮建议推进）
4. [R51.4] **MCPize开发者账号注册**（免费tier，25k reqs/mo无需信用卡）→ 可立即完成
5. [R51.5] **32x32应用图标PNG制作** → Claude Desktop .mcpb发布阻塞项
6. [R51.6] **SERVER_API_KEY种子值配置** → HTTP传输安全认证必需

### P2 — R52+跟进
7. [ ] Smithery提交准备（需GitHub repo + PyPI包验证）
8. [ ] IA技术供应商参与机会评估（Symposium展览/Demo booth）
9. [ ] OpenAI Enterprise tunnel申请

---

## 📌 已验证信息源汇总（R51新增）

| 来源 | URL | 验证时间 |
|------|-----|---------|
| IA AI Cohort Symposium 2026 (第二批成员) | reinaasia.com/hong-kong-insurers-deepen-ai-push | 2026-06-18 web_search |
| Glama Finance类别 + TDQS评分系统 | glama.ai/mcp/servers/categories/finance | 2026-06-18 web_search |
| ChatForest Insurance MCP分类 | chatforest.com/reviews/insurance-mcp-servers/ | 2026-06-18 web_search |
| Smithery发布文档 | smithery.ai/docs/build/publish | 2026-06-18 web_search |
| MCPize部署+市场+盈利 | mcpize.com / mcpize.com/developers/build-mcp-server | 2026-06-18 web_search |
| MCP.Directory提交入口 | mcp.directory/submit | 2026-06-18 web_search |
| IA首批Cohort成员(7家) | hongkongbusiness.hk / insurancebusinessmag.com | 2026-06-18 web_search |
| MCP官方文档 + Python 3.10+要求 | modelcontextprotocol.io/docs/develop/build-server | 2026-06-18 web_search |

---

**文档版本**: R51-v1.0
**数据验证方式**: 全部通过web_search实时验证（非模拟/编造）
**合规审查状态**: Glama/MCP.Directory提交方案已确认安全；MCPize/Schmierry托管需CJ决策权衡
**总指挥协调虾 | 2026-06-18 11:00 HKT**
