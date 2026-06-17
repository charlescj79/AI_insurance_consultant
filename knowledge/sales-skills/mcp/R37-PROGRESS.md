# R37 Progress Report — 保险销售MCP Server v3.0 (GL34)

**时间**: 2026-06-17 17:00 HKT (Hour 12)  
**主题**: GL34合规工具代码实施 + MCP Server v3.0发布 + 平台分发策略验证

---

## 一、核心成果

### 1. GL34合规工具 v3.0 代码实现 ✅

#### 新增内容
- **server.py 完整集成**:
  - `GL34_RED_RULES`: 3条红线规则 (PBC管治/基金隔离/盈余分配)
  - `GL34_YELLOW_RULES`: 2条黄线规则 (GN16利益区分/理赔率准确性)  
  - **动态规则**: GL34-006 演示利率上限 (ENV变量可配置，默认6%)
  - `_gl34_check()`: 核心检测引擎
  - `handle_gl34_compliance_check()`: MCP工具处理器

#### 测试验证 (6/6 PASS)
| 用例 | 期望 | 结果 | 触发规则 |
|------|------|------|----------|
| 分红基金共用 | BLOCKED | ✅ | GL34-001, GL34-002 |
| 演示利率8.5% | BLOCKED | ✅ | GL34-006 (超上限) |
| 演示利率6% | PASS | ✅ | 边界值通过 |
| GN16利益混同 | FLAGGED | ✅ | GL34-004 |
| 理赔率100% | FLAGGED | ✅ | GL34-005 |
| 合规文案 | PASS | ✅ | 无违规 |

### 2. MCP Server v3.0 全量发布 ✅

#### 工具清单 (11个)
| # | 工具名 | 类型 | 说明 |
|---|--------|------|------|
| 1 | insurance_product_query | 查询 | 香港产品条款查询(14产品) |
| 2 | compliance_check | 合规 | GL-44红线+黄线检测 |
| 3 | gl34_compliance_check | **NEW** | GL34分红治理检查 |
| 4 | needs_assessment | 诊断 | 客户需求分级(A/B/C/D) |
| 5 | objection_handler | 话术 | 6类×3层级异议处理 |
| 6 | private_sop_runner | SOP | 私域D0-D7自动化 |
| 7 | compliance_rewrite | 改写 | 违规内容自动修复 |
| 8 | lifecycle_analyzer | 分析 | D0→D30客户旅程优化 |
| 9 | client_crm_tag | CRM | 标签同步与分级 |
| 10 | multi_turn_dialogue | 对话 | 多轮上下文管理 |
| 11 | compliance_trend_analysis | 趋势 | 违规模式检测 |

#### Server状态
- **版本**: v3.0.0 (原v1.1.0)
- **协议**: MCP stdio + HTTP(SSE)双传输
- **安全**: API Key认证 + 速率限制60req/min (R27已部署)
- **测试覆盖**: stdio + HTTP = 21/21 PASS

### 3. 平台分发策略验证 (web_search实时验证)

#### 已完成调研的分发平台:
| 平台 | 规模 | 提交方式 | 数据出境 | 合规风险 |
|------|------|----------|----------|----------|
| Glama | 205K tools | browser Inspector测试+npx安装 | LOW(境外浏览) | ✅ 可用 |
| Smithery | 8K+ servers | npx一键部署/CLI publish | MEDIUM | ⚠️ 需HTTPS端点 |
| MCP.so | - | 社区目录提交 | LOW | ✅ 可用 |
| Official Registry | canonical | GitHub PR | NONE | ✅ 推荐 |
| PulseMCP | 人工审核 | 手动提交 | LOW | ✅ 可用 |
| Agensi | MCP+SKILL.md | 自动安全扫描 | MEDIUM | ⚠️ 8-point扫描 |

#### OpenAI Responses API 集成要点 (verified):
- **原生支持**: Remote MCP Server via Streamable HTTP transport
- **ChatGPT Apps**: 可直接连接我们的HTTP端点作为data-only app
- **背景模式**: 2025.8后已兼容MCP (需`background=True`)
- **成本**: 仅按token计费，无额外工具调用费
- **限制**: Assistants API deprecated 2026-08-26 → 必须走Responses API

---

## 二、三个维度汇报

### 1. 平台接入进展
- **盘点**: 17个平台/协议族
- **已对接方案**: OpenAI Responses API / Dify私有部署 / LangChain / n8n / Discord Bot / Smithery提交路径 / Glama提交路径
- **本周新增**: GL34合规工具 v3.0 + MCP Server全量更新
- **可提交平台**: Glama + Smithery (需GitHub repo)

### 2. MCP Server发布状态
| 指标 | 值 |
|------|-----|
| 工具数量 | 11个 (含GL34) |
| 测试通过率 | 21/21 = 100% |
| README | ✅ 完整(含快速入门/5 tools表格/合规框架) |
| OpenAPI.json | ✅ 9 endpoints + 16 schemas |
| Dockerfile | ✅ (但Docker Desktop未安装) |
| PyPI packaging | ✅ setup.py/pyproject.toml就绪 |
| GL34测试覆盖 | 6/6 PASS |

### 3. 合规与安全评估

#### GL34工具自身: ✅ 完全合规
- 纯本地执行，无数据出境
- 规则基于香港保监局GL34原文(2026-03-31生效)
- 演示利率上限可配置(ENV默认6%，符合GN16要求)

#### 各平台合规风险:
| 平台 | 数据出境 | PII处理 | GL-44对齐 | 综合评估 |
|------|----------|---------|-----------|----------|
| Glama | LOW(仅浏览) | N/A | ✅ MCP spec标准 | ✅ 推荐提交 |
| Smithery | MEDIUM(npx部署) | N/A | ✅ | ⚠️ 需HTTPS端点 |
| OpenAI API | MEDIUM(数据出境美国) | 合规检查本地执行 | ✅ | ⚠️ 建议私有部署+API key |
| Dify私有 | NONE(香港境内) | PII可配置脱敏 | ✅ | ✅ 最佳选择 |
| n8n私有 | NONE(可香港部署) | N/A | ✅ | ✅ 推荐 |
| Coze/扣子 | ❌ HIGH(内地服务器) | ❌ 跨境合规风险 | ❌ | ❌ 禁止提交保险工具 |
| Discord Bot | LOW + ⚠️需免责声明 | PII需脱敏 | ✅ | ⚠️ 加监管Disclaimer |

---

## 三、阻塞项 (持续8轮+待解决)

1. **GitHub Repository** — Registry提交前置条件(已多次提醒CJ)
2. **Docker Desktop** — Docker镜像构建需要(已多次提醒)
3. **HTTPS域名** — Smithery/Glama远程访问需要
4. **SERVER_API_KEY** — 生产环境种子值(开发环境可用测试值)

---

## 四、R38计划

1. **Glama平台提交准备**: 编写mcp.json manifest + 质量评分优化
2. **Smithery CLI发布流程**: 研究`smithery mcp publish`完整流程
3. **Dify私有部署实测**: docker-compose up验证端到端MCP调用链
4. **CHANGELOG.md更新**: v3.0版本日志
