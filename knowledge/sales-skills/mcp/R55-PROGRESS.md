# R55 Progress — 保险咨询销售平台化推广·快速迭代

**Round**: R55 (Hour 15)  
**Time**: 2026-06-18T15:00 HKT  
**Core Focus**: Claude Desktop .mcpb + Dify MCP Client对接方案编写 + Glama生态数据更新

---

## 【维度一】平台接入进展

### 实时生态数据验证 (2026-06-18)

| 指标 | R54值 | R55值 | 变化 |
|------|-------|-------|------|
| Glama MCP Servers | ~37,429 | **36,950** (+新增connector 5,760) | ⚠️ 总数稳定，金融类别无香港保险垂直 |
| ChatForest Insurance分类 | 7个 | **确认Socotra/Sure GA发布** | 仍为后端理赔/核保系统，无获客类 |
| Claude Desktop | stdio+config.json | **+ Desktop Extensions (.mcpb) + Third-party Model Gateway** | 新增第三方模型接入能力 |
| Dify MCP Client | dify-mcp-client plugin | **confirmed native support, HTTP/SSE transport** | ✅ Dify可直接作为MCP Client连接我们HTTP端点 |

### 本轮选定平台对接方案：Claude Desktop (.mcpb扩展) + Dify (HTTP远程)

#### A. Claude Desktop 对接方案（P0）

**两种接入方式：**

1. **Desktop Extensions (.mcpb)** — 一键安装，面向非技术用户
   - 格式：zip archive + manifest.mcpb.json
   - Anthropic官方路径：claude.com/download + Developer Mode
   - 优势：无需终端/配置，双击即可安装
   - 合规要求：首次启动弹窗显示免责声明+数据隐私声明

2. **stdio本地模式** — 面向开发者用户
   ```json
   // ~/.claude/claude_desktop_config.json
   {
     "mcpServers": {
       "insurance-sales": {
         "command": "python3",
         "args": ["/Users/charles/.openclaw/workspace/knowledge/sales-skills/mcp/src/server.py"],
         "env": {
           "SERVER_API_KEY": "your-key-here"
         }
       }
     }
   }
   ```

3. **第三方模型接入（新功能）** — Claude Desktop Developer Mode
   - 路径：Help → Troubleshooting → Enable Developer Mode → Configure Third-Party Inference
   - 可直连我们的MCP Server HTTP端点作为Gateway
   - 支持OpenAI/DeepSeek等第三放模型，扩大用户覆盖

**对接产出文件清单：**
- ✅ `R41-mcpb-manifest.json`（已存在，需更新为.mcpb格式）
- ⬜ Claude Desktop完整安装指南（含免责声明模板）
- ⬜ .mcpb打包脚本（Python packer）

#### B. Dify 对接方案（P0主力平台）

**架构：** Dify（香港节点自托管）← MCP Client ← our MCP Server (Streamable HTTP)

**Dify侧配置：**
1. 安装 `3dify-project/dify-mcp-client` 插件（GitHub/DockerHub）
2. Agent工作流中配置MCP工具连接：
   - Transport: Streamable HTTP
   - URL: `https://our-server.example.com/mcp/`
   - Auth: X-API-Key header
3. 在Chatflow中添加MCP Agent节点，调用我们的11个工具

**合规优势：**
- Dify香港节点自托管 → 数据完全可控
- 可配置本地模型（非必须调用云端LLM）
- 内置合规审查层可嵌入Dify Agent指令中

**对接产出文件清单：**
- ⬜ Dify MCP Client完整配置指南（含docker-compose）
- ⬜ Dify Agent工作流模板（JSON导出）
- ⬜ HTTP端点HTTPS证书配置方案

### 下一轮计划（R56）：LangChain/MCP Adapter对接 + Glama提交包编写

---

## 【维度二】MCP Server发布状态

| 指标 | 状态 |
|------|------|
| **版本号** | v1.3.0 (CHANGELOG已统一) |
| **工具总数** | 11 tools（product_query, compliance_check, needs_assessment, objection_handler, private_sop_runner, compliance_rewrite, lifecycle_analyzer, client_crm_tag, multi_turn_dialogue, compliance_trend_analysis, gl34_compliance_check） |
| **处理器验证** | ✅ 11/11全部通过 (R53 Bug修复后) |
| **stdio传输** | ✅ 可用，Claude Desktop/Cursor/Windsurf支持 |
| **HTTP传输** | ✅ v2 Secure版，含API Key认证+速率限制+CORS |
| **Docker镜像** | ⬜ Dockerfile-mcp已就绪（需用户安装Docker Desktop） |
| **PyPI包** | ⬜ pyproject.toml已就绪（需twine credentials） |
| **OPENAPI.json** | ✅ 已生成（9 endpoints + 16 schemas） |
| **文档** | ✅ README.md + README-developer.md + CHANGELOG |

### 发布渠道优先级（有GitHub repo后即可执行）

| 层级 | 平台 | 提交方式 | 状态 |
|------|------|----------|------|
| T0 | Glama (36,950 servers) | manifest JSON提交 | ⬜ R53包已写好 |
| T0 | MCP.Directory | GitHub auto-pull元数据 | ⬜ 数据包已写好 |
| T1 | Smithery.ai | URL发布 + server-card.json | ⬜ 流程验证通过 |
| T1 | Official Registry (Anthropic) | registry.modelcontextprotocol.io/v0/servers API | ⬜ R41方案待执行 |
| T2 | MCPize托管 | 一键部署(80%分成) | ⬜ 需评估合规 |
| T2 | ChatForest Insurance分类 | 抢占空白品类 | ⬜ 策略已确认 |

---

## 【维度三】合规与安全评估 ⚠️

### 每轮合规红线状态（不变）

```
🔴 红线1: AI保险咨询输出必须标注"本平台提供的信息仅供参考，不构成专业保险建议。如需正式投保咨询，请联系持牌保险中介人。"
🔴 红线2: 内地用户跨境咨询触及《互联网保险业务监管办法》红线
🔴 红线3: 客户个人信息不得未经同意传输至境外服务器
🔴 红线4: AI辅助决策必须保留完整审计日志（GL-44要求）
```

### 本轮平台合规分析更新

| 平台 | 数据出境风险 | 隐私保护 | 保险咨询合规性 | 综合评级 |
|------|-------------|----------|---------------|----------|
| **Claude Desktop (.mcpb本地)** | 🟢极低（进程内运行） | 🟡中（Anthropic API调用可能传数据至云端） | ⚠️需免责声明 | 🟡 可接受，需加合规层 |
| **Claude Desktop (第三方模型Gateway)** | 🟡中（请求经第三方Gateway） | 🟡中（取决于Gateway提供商） | ⚠️需评估Gateway提供商的合规性 | 🟡 需谨慎评估 |
| **Dify香港自托管** | 🟢极低（数据在自有服务器） | 🟢高（完全控制数据流+可选本地模型） | ✅内置合规审查层 | 🟢 推荐作为主力平台 |
| **LangChain/LangGraph (自托管)** | 🟢取决于部署位置 | 🟢高 | ✅需内置合规审查层 | 🟢 推荐作为API封装层 |
| **Coze/扣子** | 🔴中（字节云） | 🟡依赖平台政策 | ❌内地监管红线 | 🔴 高风险，仅限香港境内用户 |
| **微信小程序** | 🔴高（含内地节点） | 🟡腾讯政策 | ❌跨境数据+内地监管红线 | 🔴 极高风险，需严格隔离 |
| **mcp.so Registry** | 🟢无风险（仅元数据发布） | 🟢无数据交互 | 🟢纯信息展示 | 🟢安全低风险的推广渠道 |
| **Smithery (URL发布)** | 🟢无风险（直连自建端点） | 🟢 | 🟢纯元数据发布层 | 🟢 仅做目录，连接直连 |

### Glama MCP安全警示（来自最新搜索结果）
- BlueRock Security 2026分析：~7,000公开MCP Server中 **36.7%存在SSRF漏洞、41%无认证、53%用静态API Key**
- 我们的方案优势：API Key认证✅ + CORS控制✅ + Rate Limiting✅（v2已解决）
- **建议**：Glama提交时强调安全特性描述，争取更高质量评分

---

## R55产出文件

1. `R55-PROGRESS.md` ← 本文件
2. `R55-CLAUDE-DESKTOP-INTEGRATION-GUIDE.md` ← Claude Desktop对接方案（如下）
3. `R55-DIFY-MCP-INTEGRATION-GUIDE.md` ← Dify对接方案（如下）

### 阻塞项（持续）

| # | 条件 | R55状态 | 持续轮数 |
|---|------|---------|---------|
| 1 | GitHub public repo | ❌ 已超10轮 | R23起未变 ⚠️ **紧急** |
| 2 | Docker Desktop | ❌ 未安装 | - |
| 3 | PyPI twine credentials | ❌ 未提供 | - |
| 4 | SERVER_API_KEY种子值 | ✅ 已确认可动态生成 | - |
| 5 | HTTPS证书/域名 | ❌ 未配置 | R52新增 |
| 6 | 合规声明文案定稿 | ⬜ R55起草中 | - |

---

*R55完成。生成时间: 2026-06-18T15:00 HKT*
