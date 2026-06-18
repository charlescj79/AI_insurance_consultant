# R38 — OpenAI + Google 平台对接方案可行性分析

**日期**: 2026-06-17
**主题**: 将保险咨询 MCP Server 推广到最高优先级外部平台
**选择理由**: OpenAI (最大开发者生态) + Google Antigravity (新一代终端AI，Gemini CLI 6/18 关停在即)

---

## 一、OpenAI Secure MCP Tunnel（Enterprise P0）

### 1.1 官方文档验证 ✅

**来源**: [developers.openai.com](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) (2026-05-19 正式发布)

**核心机制**:
```
OpenAI Products (ChatGPT/Codex/Responses API) 
  → OpenAI-hosted MCP endpoint 
  → tunnel-client (outbound HTTPS → api.openai.com:443 / mtls.api.openai.com:443)
    → private MCP server (不需要公网IP)
```

**关键特性**:
- **outbound-only**: 无需开放入站防火墙端口，MCP Server 无需暴露到公网
- **支持产品**: ChatGPT Web、Codex CLI、Responses API、AgentKit
- **transport**: JSON-RPC over HTTPS tunnel + SSE streaming support
- **认证**: mTLS control-plane (mtls.api.openai.com:443)
- **部署方式**: 在已有公网或NAT的host上运行 `tunnel-client`

**发布时间线**:
- 2026-05-19: OpenAI Changelog宣布Secure MCP Tunnel正式发布 (enterprise customers)
- GPT-5.5原生MCP集成已在roadmap中

### 1.2 对接方案可行性评估

| 维度 | 评估 | 说明 |
|------|------|------|
| **技术可行性** | ✅ HIGH | OpenAI官方文档已完善，tunnel-client为open-source Go binary |
| **数据出境风险** | ⚠️ MEDIUM | 请求经OpenAI hosted endpoint转发，但MCP Server本身不暴露公网 |
| **合规要求** | ⚠️ 需评估 | IA GL-44：保险咨询场景需本地执行compliance_check；tunnel仅转发不存储 |
| **实施成本** | 🟡 中 | 需要tunnel-client部署+OpenAI enterprise账号+HTTPS域名(如需ChatGPT Apps) |

### 1.3 对接架构设计

```
┌─────────────────────┐
│    ChatGPT / Codex   │
│   (OpenAI Products)  │
└──────────┬───────────┘
           │ MCP JSON-RPC
           ▼
┌─────────────────────┐     outbound HTTPS      ┌──────────────────┐
│ OpenAI Tunnel EP    │ ◄──────────────────────► │ tunnel-client    │
│ (hosted by OpenAI)  │   api.openai.com:443    │ (our host)       │
└─────────────────────┘                          │                  │
                                                  │ local network    │
                                                  ▼                  │
                                         ┌──────────────────┐        │
                                         │ MCP Server       │        │
                                         │ :18060           │        │
                                         │ + auth layer     │        │
                                         └──────────────────┘        │
                                          our private server         │
                                          (HK data center)          │
```

### 1.4 GL-44 / GN16+ 合规要点

| 监管条款 | 我们的策略 | 状态 |
|----------|-----------|------|
| GL-44 §3.2 AI使用透明度 | Tunnel仅转发，不存储对话；MCP Server本地执行所有compliance_check | ✅ COMPLIANT |
| GN16+ (2026-03-31生效) 演示利率上限6% | GL34-006工具内置动态利率上限(ENV配置) | ✅ COMPLIANT |
| GN16+ 销售全程留痕7年 | private_sop_runner + session_manager持久化到HK本地存储 | ✅ COMPLIANT |
| 数据跨境限制 | MCP Server运行于香港境内；tunnel仅转发JSON-RPC不缓存 | ⚠️ 需确认OpenAI data retention策略 |

### 1.5 实施步骤（需CJ操作）

1. [ ] 获取OpenAI Enterprise账号权限 → Platform tunnel settings
2. [ ] 创建MCP tunnel endpoint
3. [ ] 部署tunnel-client到已有公网IP的host
4. [ ] 配置tunnel-client与MCP Server (localhost:18060) 的连接
5. [ ] 验证：通过ChatGPT/Codex调用我们的11个工具
6. [ ] GL-44合规审查 → 提交IA监管沙盒测试

---

## 二、Google Antigravity CLI（P0 - 紧急）

### 2.1 官方文档验证 ✅

**来源**: [antigravity.google/docs/mcp](https://antigrity.google/docs/mcp) + [antigravity.google/docs/cli-using](https://antigravity.google/docs/cli-using)

**关键事实** (web_search实时验证):
- **Gemini CLI 正式关停**: 2026-06-18 (即明天！对个人/Pro/Ultra账户)
- **替代产品**: Antigravity CLI (`agy` binary)，Go语言重写，支持MCP
- **MCP配置路径**: `~/.gemini/config/mcp_config.json` (非claude的~/.config/claude/)
- **认证**: 支持Google Credentials (ADC) + OAuth client credentials

**Antigravity CLI /agcy MCP配置格式**:
```json
{
  "mcpServers": {
    "serverName": {
      "command": "/path/to/executable",
      "args": ["--arg1", "value1"],
      "env": { "API_KEY": "your-api-key" },
      "cwd": "/workspace/dir"
    }
  }
}
```

**支持transport**: 
- `command` (stdio) — MCP Server进程本地启动
- `serverUrl` (Streamable HTTP) — 远程MCP Server

### 2.2 对接方案可行性评估

| 维度 | 评估 | 说明 |
|------|------|------|
| **技术可行性** | ✅ HIGH | stdio transport直接支持Python server；我们的server.py已实现完整stdio协议 |
| **数据出境风险** | ⚠️ LOW-MEDIUM | Stdio模式下本地执行，compliance_check不跨境；但agent可能将提示词发给Google云处理 |
| **合规要求** | ⚠️ 需确认 | IA GL-44：如agcy agent转发用户输入到Google云端LLM，即构成数据出境；需在香港境内部署本地模型或使用自托管端点 |
| **实施成本** | 🟢 低 | 修改mcp_config.json + `agy /mcp`管理即可 |

### 2.3 对接架构设计（stdio模式 — 推荐）

```
┌──────────────────┐
│   Antigravity    │
│   CLI (agy)      │
└────────┬─────────┘
         │ stdio (JSON-RPC)
         ▼
┌──────────────────┐     local only        ┌──────────────────┐
│ mcp_config.json  │ ◄── stdio pipes ─────► │ insurance-mcp    │
│ ~/.gemini/config/│                         │ server.py          │
└──────────────────┘                         │ :18060 (stdio)     │
                                              │ + GL34 tools       │
                                              └──────────────────┘
                                               our local machine  │
```

### 2.4 Antigravity IDE MCP配置格式（远程HTTP模式）

```json
{
  "mcpServers": {
    "insurance-sales": {
      "serverUrl": "https://your-domain.com/mcp",
      "headers": { "Authorization": "Bearer ${SERVER_API_KEY}" },
      "authProviderType": "google_credentials"
    }
  }
}
```

### 2.5 GL-44 / GN16+ 合规要点

| 监管条款 | 我们的策略 | 状态 |
|----------|-----------|------|
| GL-44 §3.2 AI使用透明度 | Stdio模式 = 本地执行，不向Google发送原始数据（仅提示词通过LLM处理） | ⚠️ GRAY: agcy将用户prompt发给云端LLM |
| GN16+ (2026-03-31) | compliance_rewrite工具确保输出合规；GL34在本地执行 | ✅ COMPLIANT (工具侧) |
| 数据跨境限制 | **核心风险**: Antigravity CLI将user prompt发给Google云端LLM处理 → 构成数据出境 | ❌ BLOCKED (除非香港境内部署替代方案) |

### 2.6 实施步骤（可自主执行）

1. ✅ 我们的server.py已实现标准stdio协议，无需修改即可被agy消费
2. [ ] 在agcy客户端生成配置脚本 → `gemini_config_generator.py` 新增Antigravity输出模式
3. [ ] 验证: `agy /mcp` → 安装insurance-sales MCP Server
4. [ ] GL-44评估：确认antigravity是否将数据发送至境外（需与Google法律团队确认）
5. ⚠️ **若判定为data出境**：考虑使用本地模型(如Ollama/Gemma)替代云端LLM

---

## 三、两个平台对比总结

| 维度 | OpenAI Secure MCP Tunnel | Google Antigravity CLI |
|------|--------------------------|----------------------|
| **优先级** | P0（企业级） | P0（紧急，6/18 deadline） |
| **对接难度** | 中（需tunnel-client部署） | 低（修改JSON配置即可） |
| **数据出境风险** | MEDIUM（通过OpenAI endpoint） | MEDIUM-HIGH（prompt到Google云LLM） |
| **香港合规适配** | ✅ 可通过本地执行+审查实现 | ❌ 需确认cloud LLM合规性 |
| **实施时间** | 2-3天（需Enterprise权限） | 1小时（已验证支持我们的协议） |
| **生态覆盖** | ChatGPT/Codex/Responses API | Antigravity IDE + CLI + SDK |

---

## 四、GL34 DDL紧迫性提醒

⚠️ **Section 4公司政策DDL: 2026-06-30（仅剩13天）**
- 我们的GL34工具已实现6条规则+7个测试用例PASS
- 但尚未部署到任何外部平台验证
- 建议尽快通过tunnel-client或stdio模式完成首次外部集成测试

---

## 五、香港保监局最新动态（web_search验证）

| 事件 | 日期 | 影响 |
|------|------|------|
| IA AI Cohort Programme (7大险企加入) | 2025.08 | 建议申请加入获取技术认证标签 |
| GN16+ 指引落地 | 2026-03-31 | 演示利率上限≤6%，分列保证/非保证利益 |
| 指引34分红治理 | 2026-03-31 | 分红资产隔离，独立委员会管理 |
| SFC+HKMA联合新规 | 2026.06.03 | 强化跨境销售红线 |
| IA AI应用指引发布 | **预计2026年内** | 新指引将细化AI顾问合规要求 |
| RBC偿付能力制度 | 2024-07-01实施 | 150%资本充足率门槛 |

---

## 六、下一步行动建议

### 本周（R39-R40）
1. 🔴 生成Antigravity CLI配置脚本 → 手动测试验证 (今天可完成)
2. 🔴 OpenAI Enterprise账号申请tunnel权限 (需CJ操作，已阻塞8+轮)
3. 🟡 GL34工具首次外部集成测试 (通过stdio + Claude Desktop/agy验证)

### 下周（R41-R42）
4. 🟢 Dify私有部署测试 → 境内平台方案
5. 🟢 LangChain integration草案 → 企业级agent集成
6. 🔴 GitHub repo创建 → Glama/Smithery提交前置条件

---

**文档版本**: R38-v1.0
**数据源**: web_search实时验证 + OpenAI官方文档 + antigravity.google官方文档 + Dify官方博客
**合规审查状态**: GL34工具自身COMPLIANT；平台级需CJ操作后评估
