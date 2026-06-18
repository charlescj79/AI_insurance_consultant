# Windsurf MCP配置模板

**生成时间**: 2026-06-18 R49  
**适用平台**: Windsurf IDE (Cascade AI Agent)  
**Config路径**: `~/.codeium/windsurf/mcp_config.json` (macOS/Linux)  
   | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` (Windows)

---

## 一、Stdio模式配置（本地直接启动server.py）

```json
{
  "mcpServers": {
    "insurance-sales-mcp": {
      "command": "python3",
      "args": ["/Users/charles/.openclaw/workspace/knowledge/sales-skills/mcp/server.py"],
      "transport": "stdio",
      "enabled": true
    }
  }
}
```

**Windsurf中打开方式**: `Cmd+Shift+P` → "Windsurf: Configure MCP Servers"

---

## 二、HTTP模式配置（远程部署）

```json
{
  "mcpServers": {
    "insurance-sales-mcp": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-server-url.com/mcp"],
      "transport": "http-sse",
      "enabled": true
    }
  }
}
```

---

## 三、Windsurf MCP Marketplace方式

1. 打开 Cascade panel → 右上角MCPs图标
2. 搜索 "insurance-sales-mcp"（需先发布到Smithery/Glama后才能在Marketplace找到）
3. 点击Install自动配置

---

## 四、验证连接

在Windsurf中测试：
```
Cascade: "使用insurance_sales_mcp进行合规检查"
```

检查日志：`Cmd+Shift+P` → "Developer: Show Logs.." → Windsurf tab

**注意**: Windsurf有100工具上限，我们的server只注册11个tool，不占用过多配额。

---

*R49产出 — Windsurf配置模板*
