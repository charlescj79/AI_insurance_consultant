# R53 — Glama.ai + MCP.Directory 提交包（发布就绪）

## 一、Glama.ai 提交元数据

### 提交目标
平台: https://glama.ai  
品类抢占: "Hong Kong Insurance Lead Gen MCP Server"（该分类目前完全空白）

### Glama Submission Manifest

```json
{
  "name": "insurance-sales-mcp",
  "description": "Insurance Sales MCP Server — 11 specialized tools for Hong Kong insurance private-domain lead generation, compliance checking (GL-44/GL34/GN16), and client lifecycle management.",
  "category": "finance",
  "subcategory": "insurance",
  "transport": ["stdio", "streamable-http"],
  "url": "https://github.com/<YOUR-ORG>/insurance-sales-mcp",
  "logo": "https://raw.githubusercontent.com/<YOUR-ORG>/insurance-sales-mcp/main/icon.png",
  "tools": [
    {
      "name": "insurance_product_query",
      "description": "Query HK insurance product clauses (coverage, exclusions, compliance notes). Supports fuzzy matching."
    },
    {
      "name": "compliance_check",
      "description": "14 red-line + 4 yellow-line automated compliance scan (GL-44/GN16). Returns BLOCKED/FLAGGED/PASS."
    },
    {
      "name": "needs_assessment",
      "description": "Customer needs diagnosis: risk signal extraction, customer grading (A/B/C/D), urgency rating."
    },
    {
      "name": "objection_handler",
      "description": "6 objection categories × 3 tiers response script generator."
    },
    {
      "name": "private_sop_runner",
      "description": "Private domain Day-0 to Day-7 customer follow-up SOP executor."
    },
    {
      "name": "compliance_rewrite",
      "description": "Auto-fix violating content, return before/after comparison + verification."
    },
    {
      "name": "lifecycle_analyzer",
      "description": "D0→D30 customer lifecycle analysis: awareness/trust/solution/decision/convert 5-stage model."
    },
    {
      "name": "client_crm_tag",
      "description": "Multi-dimensional CRM tag generation (risk/intent/compliance/lifecycle) + export."
    },
    {
      "name": "multi_turn_dialogue",
      "description": "80-turn sliding window session context manager for multi-round insurance consultation."
    },
    {
      "name": "compliance_trend_analysis",
      "description": "Historical compliance violation trend analysis + rule statistics + improvement suggestions."
    },
    {
      "name": "gl34_compliance_check",
      "description": "GL34 participating policy governance check (2026-03-31 effective): PBC structure, fund isolation, surplus distribution fairness, GN16 benefit differentiation, claim ratio accuracy, illustration rate cap."
    }
  ],
  "license": "MIT",
  "author": "Clawsure Insurance Tech Team",
  "tags": ["insurance", "hong-kong", "compliance", "regtech", "GL-44", "GL34", "lead-generation", "private-domain"]
}
```

### Glama 提交步骤
1. Visit https://glama.ai/new (或 submit 入口)
2. Paste the manifest above
3. Provide GitHub repo URL (after creating org/repo)
4. Upload icon.png (32x32 or 64x64 PNG)

### 先发窗口分析
- Glama Finance category: 无香港保险垂直MCP Server（当前约37,000+ servers）
- 竞品空白确认：ChatForest Insurance分类仅有理赔/核保后端系统
- **抢占策略**：在Glama上注册为"Insurance → Hong Kong Lead Gen"品类的第一名

---

## 二、MCP.Directory 提交数据

### MCP.Directory 元数据 (JSON)

```json
{
  "name": "insurance-sales-mcp",
  "description": "保险咨询销售全链路MCP Server — 11 tools for HK insurance lead generation, compliance checking, and client lifecycle management.",
  "url": "https://github.com/<YOUR-ORG>/insurance-sales-mcp",
  "repository": {
    "provider": "github",
    "owner": "<YOUR-ORG>",
    "repo": "insurance-sales-mcp"
  },
  "logoUrl": "/icon.png",
  "category": "finance",
  "subcategory": "insurance",
  "tools": [
    {"name": "insurance_product_query", "description": "HK insurance product query"},
    {"name": "compliance_check", "description": "GL-44/GL34 compliance scanner"},
    {"name": "needs_assessment", "description": "Customer needs diagnosis"},
    {"name": "objection_handler", "description": "Objection handling scripts"},
    {"name": "private_sop_runner", "description": "Private domain SOP executor"},
    {"name": "compliance_rewrite", "description": "Auto-compliance fix"},
    {"name": "lifecycle_analyzer", "description": "Customer lifecycle analysis"},
    {"name": "client_crm_tag", "description": "CRM tag generator"},
    {"name": "multi_turn_dialogue", "description": "Multi-turn session manager"},
    {"name": "compliance_trend_analysis", "description": "Compliance trend analyzer"},
    {"name": "gl34_compliance_check", "description": "GL34 participating policy compliance"}
  ],
  "auth": {
    "type": "none",
    "docsUrl": "/docs/SECURITY.md"
  },
  "tags": ["insurance", "hong-kong", "compliance", "regtech", "GL-44", "lead-gen"]
}
```

### MCP.Directory 提交步骤
1. Visit https://mcp.directory/publish
2. Connect GitHub account
3. Auto-pulls repository metadata (24h sync)
4. **优势**：零配置，自动追踪GitHub repo更新

---

## 三、前置条件清单（阻塞项）

| # | 条件 | 状态 | 预计耗时 | 依赖方 |
|---|------|------|---------|--------|
| 1 | GitHub public repo | ❌ 未创建 | 5min | CJ (CJ) |
| 2 | 32x32 icon PNG | ❌ 未提供 | 2min | CJ (CJ) |
| 3 | Glama account注册 | ✅ 可自助完成 | 2min | R46执行者 |
| 4 | MCP.Directory GitHub连接 | ⏳ 依赖#1 | <1min | R46执行者 |

### 🚀 一键提交脚本（有GitHub repo后）

```bash
#!/bin/bash
# submit-to-registries.sh — 需要先创建GitHub repo
REPO_URL="https://github.com/<YOUR-ORG>/insurance-sales-mcp"
ICON_URL="${REPO_URL}/raw/main/icon.png"

echo "=== Glama Submission ==="
echo "1. Visit https://glama.ai/new"
echo "2. Paste R53-GLAMA-SUBMISSION-PACK.md 中的 manifest JSON"
echo "3. Set url=${REPO_URL}, logo=${ICON_URL}"

echo ""
echo "=== MCP.Directory Submission ==="
echo "1. Visit https://mcp.directory/publish"
echo "2. Connect GitHub → auto-syncs your repo metadata"
echo "3. 24h after first sync, your server will appear in directory"

echo ""
echo "=== Smithery (备选) ==="
echo "Visit https://smithery.ai/new → paste HTTPS endpoint URL"
echo "No OAuth needed for metadata-only publish"
```

---

## 四、品类抢占策略（核心洞察）

### 当前市场空白地图
```
Glama (37,429 servers)
├── Finance category
│   ├── ❌ 香港保险获客 = 无竞品 ← 我们的品类
│   └── RegGuard(通用金融合规检查) → 不重叠
└── Insurance category
    └── ChatForest 7 servers: Socotra/ClaimsProcessing等(后端系统) ← 不重叠

ChatForest (Insurance 分类)
├── ❌ 香港保险获客 = 无竞品 ← 我们的品类
└── 全部理赔/核保/GA后端 → 不重叠

Official Registry (registry.modelcontextprotocol.io)
└── ❌ 香港保险垂直 = 无竞品 ← 我们的品类
```

### 抢占建议
1. **在Glama注册时指定 subcategory = "insurance" + tag = ["hong-kong", "lead-generation"]**
2. **在MCP.Directory也提交**，形成双目录覆盖
3. **品牌定位**："First MCP Server for Hong Kong Insurance Lead Generation"

---

## 五、合规声明（Glama/MCP.Directory公开版）

> ⚠️ **Disclaimer**: This server provides reference information only and does NOT constitute professional insurance advice. For formal insurance consultation, please contact a licensed insurance intermediary. All compliance checking is based on Hong Kong Insurance Authority guidelines (GL-44, GL34, GN16). Cross-border insurance sales to mainland China residents may violate PRC financial regulations.
>
> 📋 **Data Policy**: All processing runs locally or in your own deployment. No telemetry, no analytics, no data collection.

---

*R53 产出。提交包已就绪，等待GitHub repo创建即可执行发布。*
*生成时间: 2026-06-18T14:00 HKT*
