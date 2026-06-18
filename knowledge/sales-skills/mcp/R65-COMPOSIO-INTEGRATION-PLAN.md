# Composio 集成方案 — R65 交付物

**生成时间**: 2026-06-18T20:00 HKT  
**状态**: ✅ 方案设计完成，等待 CJ 决策

---

## 一、Composio 平台定位确认（实时验证）

### Composio v2026 现状
| 指标 | 数据源 | 数值 |
|------|--------|------|
| GitHub Stars | ComposioHQ/composio repo | ~28,000 stars / 4,542 forks |
| Toolkits / Tools | ChatForest + docs.composio.dev (May 2026) | ~982 toolkits / 20,000+ tools / 500+ apps |
| 融资额 | Lushbinary MCP Guide | $29M ($4M seed + $25M Series A, Lightspeed领投) |
| Tool Router | ChatForest review (May 3, 2026) | GA状态，替代了之前的Rube产品 |
| mcp.composio.dev | Composio docs | **已废弃**，使用 backend.composio.dev/v3/mcp/ |

### 关键发现
- Composio MCP Server 不再使用 SSE 传输，改用 **User-scoped MCP URLs**（每用户独立预签URL）
- 新组织需通过 API key 访问（2026.03.05起强制）
- OpenAI Python SDK 原生支持 Composio MCP: `client.responses.create(tools=[{type:"mcp", ...}])`
- **Composio 本身不提供保险咨询工具** — 它是桥接层，连接已有的500+ SaaS app

---

## 二、我们的MCP Server + Composio 集成策略

### 方案：将保险MCP作为 "Custom Toolkit" 注册到 Composio

#### 架构设计
```
AI Client (Claude/Cursor) → Composio MCP Gateway 
    → user-scoped session URL 
    → Insurance Sales MCP (自托管香港VPS) 
    → 保险咨询工具(本地执行+合规引擎)
```

#### 集成路径（3种可选）

**路径A: Tool Router + 自定义 HTTP Endpoint（推荐）**
- 我们的 MCP Server 以 Streamable HTTP 模式运行在香港 VPS
- 在 Composio Dashboard 注册为我们的 "Custom App"
- Composio 作为 OAuth/认证中间层，用户连接后获得 user-scoped URL
- **优势**: 利用Composio的500+ app桥接能力（CRM/Social/Payment扩展）
- **劣势**: 保险数据流经Composio托管服务 → 合规需审查

**路径B: Standalone Deployment + Composio Directory Listing**
- 不接入Composio作为代理，仅将我们的MCP提交到Composio Marketplace listing
- 作为独立的 "Hong Kong Insurance Advisor" toolkit被发现
- **优势**: 零数据出境风险，纯目录曝光
- **劣势**: 无法使用Composio的OAuth/桥接能力

**路径C: Hybrid — 仅 product_query + compliance_check 走Composio**
- CRM/SOP等敏感工具本地stdio运行
- product_query 和 GL34合规检查通过Composio Tool Router暴露
- **优势**: 平衡曝光与合规，敏感数据不出境
- **劣势**: 架构复杂度提升

### 推荐：路径C (Hybrid)

| 维度 | 路径A | 路径B | 路径C(推荐) |
|------|-------|-------|------------|
| 开发成本 | 中 | 低 | 中 |
| 合规风险 | 🟡 MEDIUM | 🟢 NONE | 🟢 LOW |
| 曝光价值 | 高(500+app生态) | 中(directory) | 中高 |
| 可扩展性 | 最高(桥接所有app) | 低(静态列表) | 中 |

---

## 三、合规风险分析（Composio专属）

### 数据流评估
| 环节 | 数据存储地 | PDPO合规 | GL-44合规 | 保险咨询红线 |
|------|-----------|----------|-----------|-------------|
| **用户连接OAuth** | Composio云端(美国) | ⚠️ 跨境传输需用户同意 | ⚠️ 凭证管理第三方托管 | 🟢 不涉及 |
| **Tool Router session URL** | 预签名URL(短期有效) | ⚠️ 经Composio路由 | ⚠️ API key经第三方 | 🟡 需注意 |
| **保险咨询数据** | → 我们的VPS | ✅ 最终落点本地 | ✅ 合规引擎本地 | ✅ 符合GL-44 |

### 合规建议
1. **路径C**: 仅暴露 product_query (只读) + compliance_check (只读规则库) → 最小化数据出境
2. 所有 client_crm_tag / private_sop_runner / multi_turn_dialogue 等含客户数据的工具 **保持本地stdio**
3. 用户需签署 PDPO 跨境数据传输同意书（若使用路径A/B）
4. 在Glama提交时明确标注: "Data processing happens locally; Composio integration optional"

---

## 四、执行清单

### CJ 需决策
| # | 决策项 | 选项 |
|---|--------|------|
| 1 | 是否注册Composio账号 | ✅ 建议注册（免费层支持50+ app） |
| 2 | 选择集成路径 | PathA(全桥接) / PathB(仅目录) / PathC(Hybrid推荐) |
| 3 | VPS部署就绪时间 | 影响Composio连接测试日期 |

### 开发步骤（PathC方案）
1. [ ] CJ: 创建 Composio 账号 (free tier, dashboard.composio.dev)
2. [ ] CJ: 获取 API Key (Settings → API Keys)
3. [ ] 编写 `composio_integration.py` — 将我们的MCP注册为Composio custom toolkit
4. [ ] 本地测试 Tool Router 连接
5. [ ] 提交到 Composio Marketplace listing

### 前置依赖
- Compo sio API Key（CJ提供）
- Streamable HTTP URL（需要VPS + HTTPS，阻塞项同Glama/Smithery）
- MCP Server initialize handshake验证通过（已有代码支持）

---

## 五、与四平台提交策略的关系

| 平台 | Composio集成影响 |
|------|-----------------|
| Glama Registry | ✅ 独立 — 直接提交server-card.json |
| Smithery | ✅ 独立 — MCPB格式无需Composio |
| mcp.so | ✅ 独立 — 目录入口，可标注"支持Composio桥接" |
| awesome-mcp-servers | ✅ 独立 — PR即可 |
| **Composio Marketplace** | 🆕 新目标 — 扩展曝光面 |

---

*R65交付完成。server-card.json已更新（R65版本），Composio集成方案待CJ决策后执行。*
