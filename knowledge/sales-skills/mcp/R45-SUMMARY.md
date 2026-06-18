# R45: 三个维度汇报摘要

**时间**: 2026-06-18 02:00 HKT  
**触发**: cron定时任务 (insurance-sales-planning-weekly)

## 📍 三个维度

### 1. 平台接入进展
- **盘点总数**: 20+ 平台/协议族
- **已有方案**: 13个对接方案（含代码/文档）
- **R45新验证**: Glama Connectors(5,760), Dify v1.6+, OpenAI四端MCP全链路确认
- **关键更新**: Glama新增Connectors类别，是比Open-source Servers更丰富的分发维度

### 2. MCP Server发布状态
- **版本**: v1.3.0 (server.py 72.6KB/1534行)
- **工具数**: 11个 (5核心+GL34扩展)
- **测试**: 21/21 (100%)
- **传输**: stdio + HTTP双支持
- **安全**: API Key认证层已完成
- **文档**: README(4.5KB)+OpenAPI(9端点+16 schema)+PyPI packaging就绪

### 3. 合规与安全评估
| 维度 | 评级 | 备注 |
|------|------|------|
| Claude Desktop/Cursor (stdio) | 🟢 LOW | NONE数据出境 |
| Dify私有部署 | 🟢 LOW | NONE出境，PII可配置 |
| n8n私有部署 | 🟢 LOW | NONE出境 |
| Glama/Smithery Registry | 🟢 LOW | 仅提交，无数据交互 |
| OpenAI Responses API (MCP) | 🟡 MEDIUM | 数据出境但合规检查本地执行 |
| Coze/扣子 | ❌ BLOCKED | 跨境保险数据违法 |
| WeChat Mini Program | ❌ BLOCKED | 向内地开放保险数据违法 |

**新安全情报**: MCP Tunnels (outbound-only) 可解决HTTPS域名阻塞项 — 用Vercel/Cloudflare edge部署

## 🔴 阻塞项持续 (7+轮未变, 需CJ操作)
1. GitHub repo / Docker Desktop / HTTPS域名 / SERVER_API_KEY / PyPI凭证 / Registry API key

**🔥 R45特别建议**: MCP Tunnels是新解法 — 不需要自建HTTPS证书，Vercel edge + outbound tunnel即可满足OpenAI remote MCP需求。这是一个可行动的阻塞项突破口。
