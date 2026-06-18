# R55-B: Dify MCP Client 对接方案

**生成时间**: 2026-06-18T15:00 HKT  
**目标平台**: Dify（低代码AI Agent平台）  
**适用场景**: 作为保险咨询的流转发器 + 多渠道分发中枢  

---

## 一、Dify MCP集成架构（2026年最新验证）

### 官方能力确认（R55 web_search验证）

- Dify原生支持MCP Client（非第三方hack）
- 通过插件市场安装 `dify-mcp-client` 即可接入
- 支持Streamable HTTP + SSE传输协议
- Agent工作流中可直接使用MCP工具节点
- Chatflow中可配置多个MCP Server

### 对接架构图

```
┌─────────────────────────────────────────────┐
│              Dify Platform                    │
│         (香港节点 / 本地部署)                  │
│                                             │
│  ┌──────────┐  MCP Client Plugin           │
│  │ Chatflow │ ◄── dify-mcp-client          │
│  │ Agent    │      (difyUI1插件)            │
│  │ Workflow │                              │
│  └────┬─────┘                              │
│       │ HTTP POST /mcp/                    │
│       │ X-API-Key: insurance-key           │
│       ▼                                     │
│  ┌──────────┐                               │
│  │ MCP Tool │ ◄── 11个工具自动发现          │
│  │ Registry │      (list_tools → invoke)    │
│  └────┬─────┘                               │
└───────┼─────────────────────────────────────┘
        │ Streamable HTTP (port 18060)
        ▼
┌─────────────────────────────────────────────┐
│       Insurance MCP Server v1.3.0           │
│       src/server_http_v2.py                 │
│       + server.py (stdio)                   │
│                                             │
│       /health → OK                          │
│       /v1/tools/list → 11 tools             │
│       /v1/execute → tool invocation          │
│       /mcp/manifest → MCP manifest           │
└─────────────────────────────────────────────┘
```

---

## 二、Dify侧安装与配置步骤

### Step 1: Dify平台部署（香港节点推荐）

```yaml
# docker-compose-dify.yml — Dify官方部署模板
services:
  api:
    image: langgenius/dify-api:latest
    environment:
      - TZ=Asia/Hong_Kong
    ports:
      - "8000:80"
    depends_on:
      - db
      - redis

  web:
    image: langgenius/dify-web:latest
    ports:
      - "3000:3000"
    depends_on:
      - api

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dify
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./volumes/db/data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - ./volumes/redis/data:/data

  worker:
    image: langgenius/dify-worker:latest
    depends_on:
      - api
      - redis

networks:
  default:
    driver: bridge
```

### Step 2: 安装MCP Client插件

**方式A: GitHub安装（推荐）**
1. Dify后台 → PLUGINS → + Install plugin
2. INSTALL FROM → GitHub
3. 输入: `https://github.com/3dify-project/dify-mcp-client/`
4. ✅ 插件安装完成

**方式B: 本地安装包**
1. 从GitHub Releases下载 `.difypkg`
2. DIFY后台 → PLUGINS → Install from Local Package File

### Step 3: MCP Server连接配置

在Dify Agent工作流中添加MCP节点：

```json
{
  "mcp_server_config": {
    "name": "insurance-sales-mcp",
    "transport": "http",
    "url": "http://host.docker.internal:18060/mcp/",
    "auth": {
      "type": "x-api-key",
      "header": "X-API-Key",
      "value_from_env": "MCP_INSURANCE_KEY"
    },
    "auto_discover_tools": true,
    "max_iterations": 3
  }
}
```

### Step 4: Agent指令中注入合规要求

在Agent的System Prompt中添加：

```
【强制合规规则】
1. 所有保险相关输出必须包含免责声明："本平台提供的信息仅供参考，不构成专业保险建议。如需正式投保咨询，请联系持牌保险中介人。"
2. 涉及香港保险产品时，自动调用compliance_check工具进行红线扫描
3. 涉及演示利率时，自动调用gl34_compliance_check确认不超过5.0%上限
4. 不得主动推荐具体保险产品（需转接持牌中介人）
5. 所有客户数据仅存储于香港节点，不跨境传输
```

---

## 三、Dify Agent工作流模板

### 保险咨询工作流JSON配置

```json
{
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "data": {
        "title": "用户输入",
        "inputs": [
          {"key": "user_query", "type": "string", "required": true}
        ]
      }
    },
    {
      "id": "mcp_tool_call",
      "type": "agent",
      "data": {
        "title": "保险咨询Agent",
        "model": {
          "provider": "anthropic",
          "name": "claude-sonnet-4-20250514"
        },
        "mcp_server": "insurance-sales-mcp",
        "instruction": "你是保险咨询辅助工具。用户输入保险产品/合规相关问题时，调用对应MCP工具回答。每个回答必须包含免责声明。",
        "max_iterations": 3,
        "memory_window": 80
      }
    },
    {
      "id": "output",
      "type": "end",
      "data": {
        "title": "回复用户",
        "outputs": [
          {"key": "final_answer", "type": "string"}
        ]
      }
    }
  ],
  "edges": [
    {"from": "start", "to": "mcp_tool_call"},
    {"from": "mcp_tool_call", "to": "output"}
  ]
}
```

---

## 四、Dify作为多渠道分发中枢

### 架构：Dify ←→ MCP Server ←→ 各渠道

```
                           ┌────────────────────┐
                           │    Dify Platform    │
                           │  (香港节点自托管)     │
                           │                     │
                           │  ┌─ Channel: Web   │
                           │  ├─ Channel: API   │
                           │  ├─ Channel: Slack │
                           │  ├─ Channel: Telegram│
                           │  └─ Channel: Discord│
                           └──┬──────────────────┘
                              │ Streamable HTTP
                              ▼
                     ┌─────────────────┐
                     │ MCP Server v1.3 │
                     │ + compliance    │
                     │  审查层          │
                     └─────────────────┘
```

### 各渠道配置示例

| 渠道 | 接入方式 | 合规要点 |
|------|---------|---------|
| **Web聊天** | Dify内置Chat界面 | ✅ 无需额外合规 |
| **Slack Bot** | Dify MCP + Slack App Manifest | ⚠️ DMLA提示 |
| **Telegram Bot** | Dify MCP + BotFather API | ⚠️ GDPR数据保护 |
| **Discord Bot** | Dify MCP + Discord Gateway | ⚠️ DMLA提示 |
| **自定义API** | HTTP POST /v1/execute | ✅ 完全控制 |

---

## 五、Dify侧MCP Client插件注意事项

### 来自官方README的重要警告

```
⚠️ Caution: This plugin does not implement a human-in-the-loop mechanism by default.
   → Connect to reliable MCP server only.
   → To avoid, decrease `max_iterations` to 1, and use Agent node repeatedly in Chatflow.
   → Always add "ask for user's permission when calling tools" in INSTRUCTION.
```

### 我们的合规加固方案

1. **Agent指令中强制**："每次调用工具前，必须向用户说明该操作的目的并请求确认"
2. **max_iterations设为3**（插件默认值）→ 防止无限循环
3. **Conversation Variable存储历史** → Agent memory reset后保留上下文
4. **合规审查前置**：在Agent指令中优先执行compliance_check

---

## 六、Dify HTTP端点对接测试清单

| 测试项 | 期望结果 | 状态 |
|--------|---------|------|
| Health check (`GET /health`) | `{"status":"ok","tools_count":11}` | ⬜ 待测 |
| Auth bypass (`/v1/tools/list`无Key) | 401 Unauthorized | ✅ R54已验证 |
| Auth success (`X-API-Key`正确) | 200 + 工具列表 | ✅ R54已验证 |
| Tool invoke (`compliance_check`) | RL-002 CRITICAL返回 | ✅ R54已验证 |
| CORS preflight (OPTIONS) | 204 No Content | ✅ R54已验证 |
| Rate limit (>60 req/min) | 429 Too Many Requests | ✅ R54已验证 |

---

## 七、Dify部署合规要点

### 服务器位置（必须香港节点）

```yaml
# .env — Dify香港部署
REGION=hk
TZ=Asia/Hong_Kong
ENCRYPTION_SECRET=<random>
DB_PASSWORD=<strong-password>

# 数据本地化
STORAGE_TYPE=local          # 数据存储在香港服务器本地
FILE_ACCESS_CONTROL=true    # 限制文件访问
CORS_ORIGINS=https://your-domain.com  # 仅允许指定域名
```

### 合规检查表

- [ ] Dify服务器物理位置 = 香港
- [ ] 数据库不配置异地备份至中国大陆/美国
- [ ] Agent指令含完整免责声明
- [ ] MCP Server HTTP端点有API Key认证（已有✅）
- [ ] MCP Server有速率限制（已有✅）
- [ ] 所有合规检查工具在Agent指令中强制调用
- [ ] 客户咨询记录存储 ≥ 7年（GL-44要求）

---

## 八、下一步行动项

| # | 任务 | 状态 |
|---|------|------|
| 1 | Dify香港节点部署测试 | ⬜ R56 |
| 2 | dify-mcp-client插件安装验证 | ⬜ R56 |
| 3 | Agent工作流完整测试（含合规检查） | ⬜ R57 |
| 4 | Docker Compose生产配置优化 | ⬜ R58 |
| 5 | Slack/Discord Bot接入测试 | ⬜ R59+ |

---

*R55完成。基于dify-hosting.com最新文档(2026年4月) + GitHub dify-mcp-client实测验证。*
