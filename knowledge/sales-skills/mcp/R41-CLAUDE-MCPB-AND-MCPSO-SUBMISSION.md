# R41: Claude Desktop MCPB 扩展 + mcp.so Registry 提交方案

**时间**: 2026-06-18 08:00 HKT | **Round**: R41
**优先级**: P0 — 今日必须产出可执行文档

---

## 一、Claude Desktop MCPB 扩展（核心分发渠道）

### 1.1 现状分析

- **官方规格**: Anthropic 于2025年6月推出Desktop Extensions (.mcpb)，Team/Enterprise可用
- **GitHub Spec**: github.com/modelcontextprotocol/mcpb
- **已有产物**: `claude-desktop-config.mcpb` (已存在於mcp目录)
- **关键发现**: .mbp是zip+manifest架构，支持一键安装弹窗

### 1.2 MCPB Manifest 构建方案

```json
{
  "name": "insurance-sales-mcp",
  "version": "1.0.0",
  "description": "香港保险咨询销售AI Agent — GL-44/GL34合规 | 11个MCP工具",
  "manifestVersion": 1,
  "server": {
    "command": "python3",
    "args": ["<path>/server.py"],
    "env": {
      "SERVER_TRANSPORT": "stdio"
    }
  },
  "tools": [
    "insurance_product_query",
    "compliance_check",
    "needs_assessment",
    "objection_handler",
    "private_sop_runner",
    "compliance_rewrite",
    "lifecycle_analyzer",
    "client_crm_tag",
    "multi_turn_dialogue",
    "compliance_trend_analysis",
    "gl34_compliance_check"
  ],
  "categories": ["Finance", "Insurance", "Compliance"],
  "license": "Apache-2.0",
  "icon": "<base64-encoded-icon>",
  "homepageUrl": "https://github.com/<org>/insurance-sales-mcp",
  "privacyPolicyUrl": "https://github.com/<org>/insurance-sales-mcp/blob/main/PRIVACY.md"
}
```

### 1.3 MCPB 打包命令

```bash
cd knowledge/sales-skills/mcp/
# 创建manifest.json
# 打包为mcpb (zip + manifest)
python3 -m mcpb pack --output insurance-sales-mcp.mcpb \
  --manifest manifest.json \
  --server server.py \
  --include "src/tools/*.py" \
  --include "data/*.json"
```

### 1.4 合规声明要求（强制）

MCPB扩展必须包含以下合规元素：

1. **免责声明**（首次安装弹窗显示）:
   > "本平台提供的信息仅供参考，不构成专业保险建议。如需正式投保咨询，请联系持牌保险中介人。"

2. **数据隐私声明**:
   - 所有会话数据仅存储在本地
   - 不向任何第三方传输客户信息
   - API Key由用户自行管理

3. **目标用户限定**:
   - 仅限香港持牌保险中介人使用
   - 不可用于内地客户保险销售

### 1.5 分发路径

| 路径 | 方式 | 状态 |
|------|------|------|
| Claude Desktop手动安装 | .mcpb文件 + manifest.json | ✅ 可立即执行 |
| Glama平台发布 | npx一键安装 | 待GitHub repo |
| Smithery发布 | smithery publish | 待HTTPS端点 |

---

## 二、mcp.so (Official MCP Registry) 提交方案

### 2.1 mcp.so 平台确认

- **注册表**: registry.modelcontextprotocol.io（官方）+ mcp.so
- **当前规模**: mcp.so listing 20,222 servers (RoxyAPI data)
- **提交方式**: GitHub PR / 表单提交
- **所需元数据**: name, description, categories, transport types, tool list, auth requirement, homepage URL

### 2.2 提交前准备清单

| 项目 | 状态 | 优先级 |
|------|------|--------|
| GitHub repo (public) | ❌ 未创建 | 🔥 CRITICAL |
| LICENSE (已准备Apache-2.0) | ✅ 就绪 | ✅ DONE |
| README.md (含快速开始) | ✅ 4.5KB完整 | ✅ DONE |
| package.json/pyproject.toml | ✅ v1.0.0 | ✅ DONE |
| mcp.so manifest文件 | ❌ 需创建 | P1 |
| icon (32x32 PNG) | ❌ 未创建 | P2 |

### 2.3 mcp.so 提交步骤

```bash
# Step 1: 创建mcp.so manifest (JSON)
cat > mcpso-manifest.json << 'EOF'
{
  "name": "insurance-sales-mcp",
  "description": "香港保险咨询销售MCP Server - GL-44/GL34合规引擎，11个工具覆盖产品查询、合规检查、需求评估、异议处理",
  "version": "1.0.0",
  "transport": ["stdio", "http"],
  "tools": [
    {"name": "insurance_product_query", "description": "查询香港保险产品条款"},
    {"name": "compliance_check", "description": "14红+4黄合规检查引擎"},
    {"name": "needs_assessment", "description": "客户需求分级诊断(A/B/C/D)"},
    {"name": "objection_handler", "description": "异议处理话术(6类x3级)"},
    {"name": "private_sop_runner", "description": "私人SOP Day0-7工作流"},
    {"name": "compliance_rewrite", "description": "不合规文案改写"},
    {"name": "lifecycle_analyzer", "description": "客户生命周期分析"},
    {"name": "client_crm_tag", "description": "CRM标签自动化"},
    {"name": "multi_turn_dialogue", "description": "多轮对话管理"},
    {"name": "compliance_trend_analysis", "description": "合规趋势分析"},
    {"name": "gl34_compliance_check", "description": "GL34专项合规检查(分红/治理)"}
  ],
  "auth": {
    "type": "api_key",
    "required": true,
    "description": "需要API Key认证，防止未授权访问"
  },
  "license": "Apache-2.0",
  "categories": ["Finance", "Insurance", "Compliance"],
  "homepageUrl": "https://github.com/<org>/insurance-sales-mcp",
  "documentationUrl": "https://github.com/<org>/insurance-sales-mcp/blob/main/README.md"
}
EOF

# Step 2: 通过mcp.so提交界面或PR方式提交
```

### 2.4 mcp.so 竞品分析（搜索验证）

搜索了mcp.so上所有保险相关MCP Server：**目前无直接竞品**。这是我们的窗口期。

**相近领域竞争者**:
- `bizclaw-business-directory` (通用企业查询)
- `openapi-directory-mcp` (API文档查询)
- 无任何"保险咨询/合规"类MCP Server

---

## 三、Comply AI竞对分析（情报更新）

### 3.1 竞对确认

**Comply.com** — 纽约RegTech公司，2026年4月23日发布了业界首个金融合规MCP Server。

| 对比维度 | ComplyAI (竞对) | insurance-sales-mcp (我们) |
|----------|-----------------|---------------------------|
| 发布时间 | 2026-04-23 | v1.0.0 = 就绪（更早部署可领先） |
| 目标市场 | 全球金融服务机构 | **香港保险垂直领域** |
| 合规范围 | 通用金融合规 | **GL-44 + GL34 + GN16 (香港特定)** |
| 工具数 | 未公开（预估5-8个） | **11个MCP工具 + CLI v7.0 (23命令)** |
| 数据主权 | SaaS云端 | **可本地/私有部署** |
| 中文支持 | 英文为主 | **中英双语** |
| 定价 | Enterprise (未公开) | Open-source (Apache-2.0) + 企业版可选 |

### 3.2 差异化竞争策略

1. **市场先发**: 香港保险垂直领域，无直接竞品
2. **合规深度**: GL-44/GL34/GN16三合一，非通用合规
3. **成本优势**: Open-source基础 + 私部部署 = 远低于Comply enterprise定价
4. **AI销售链路完整**: 竞品只做合规检查，我们覆盖"获客→需求评估→异议处理→SOP转化"全链路

### 3.3 行动项

- ⚠️ **加速发布**：Comply已于2026年4月进入MCP生态，必须在Q2-Q3窗口期建立品牌认知
- ✅ 考虑向IA AI Cohort Programme申请技术认证（已有10家险企加入）
- ✅ 与香港保险商会/TCSP协会合作推广

---

## 四、三维度汇报

### 【维度一】平台接入进展

| 指标 | 数值 | 说明 |
|------|------|------|
| 盘点平台数 | **23个** | +3个(Comply AI/Official Registry/mcp.so) |
| 已对接方案数 | **14个** | +2个(MCPB扩展/mcp.so提交) |
| 本周新增 | **3个** | Claude MCPB、mcp.so、Comply竞对分析 |

### 【维度二】MCP Server发布状态

- **工具总数**: 11个全部可用 ✅
- **测试通过率**: 21/21 (100%) ✅
- **发布就绪度**: P0.5（缺GitHub repo阻塞Registry提交）
- **文档完整性**: README + OpenAPI + Dockerfile + PyPI + CLI v7.0 + SKILL.md — 齐全
- **MCPB扩展清单**: manifest.json模板已写入，需创建icon

### 【维度三】合规与安全评估

| 发布渠道 | 数据出境风险 | 保险咨询合规 | 综合评级 |
|----------|-------------|-------------|----------|
| Claude Desktop (.mcpb本地) | 🟢 无（进程内） | ✅ +免责声明即可 | 🟢 推荐首选 |
| mcp.so Registry（提交后） | 🟢 仅信息展示，不传输数据 | ✅ 需平台审核合规声明 | 🟢 可接受 |
| Glama Gateway（托管模式） | 🟡 经Glama代理层 | ✅ Glama已有OAuth/gateway | 🟡 可选 |
| Smithery发布 | 🟢 npm-style分发 | ✅ 仅工具描述 | 🟢 推荐 |
| ComplyAI（竞对对标） | 🔴 Enterprise SaaS云端 | ⚠️ 通用金融合规≠香港特定 | — 不跟进 |

### 🚨 核心合规约束

1. **所有对外MCP Server必须内置合规审查层**：compliance_check工具不可移除
2. **AI输出必须标注免责声明**：非专业保险建议
3. **客户数据不得出境**：优先推荐本地/私有部署模式
4. **审计日志留存≥7年**：session_manager已实现

---

## 五、R42 行动计划（下一步）

1. ✅ **立即执行**: 编写manifest.json + MCPB打包脚本
2. ⏳ **需用户操作**: 
   - 创建GitHub public repo (提交mcp.so/Registry/Glama前置条件)
   - 生成32x32应用图标PNG
   - 确认SERVER_API_KEY种子值
3. 📋 **待推进**: Coze/扣子方案（合规风险P3，暂不执行）

---

*产出文件: R41-CLAUDE-MCPB-AND-MCPSO-SUBMISSION.md*
*R41结束*
