# R55-A: Claude Desktop 对接方案

**生成时间**: 2026-06-18T15:00 HKT  
**目标平台**: Claude Desktop (Anthropic官方桌面应用)  
**适用版本**: macOS/Windows Claude Desktop v4.0+

---

## 一、Claude Desktop MCP接入架构（2026年最新）

### 三种接入方式对比

| 接入方式 | 用户类型 | 安装复杂度 | 数据流向 | 推荐场景 |
|----------|----------|-----------|---------|---------|
| **.mcpb Desktop Extension** | 非技术用户 | ★☆☆ (双击) | 本地进程 | C端客户推广 |
| **stdio 本地配置** | 开发者 | ★★★ (手动配置) | 本地进程 | 内部团队使用 |
| **第三方模型Gateway** | 高级用户 | ★★☆ | 经第三方 | 扩大AI模型覆盖 |

---

## 二、方案A: .mcpb Desktop Extension（一键安装）

### .mcpb文件格式规范（Anthropic官方，2025年9月更新）

```
insurance-sales-mcp.mcpb/          # zip archive根目录
├── manifest.json                  # MCP Bundle清单
├── server.py                      # MCP Server代码入口
├── src/                           # 全部依赖模块
│   ├── server.py
│   ├── server_http_v2.py
│   ├── tools/
│   │   ├── product_query.py
│   │   ├── compliance_check.py
│   │   └── ... (9 more)
│   └── ...
├── data/                          # 知识库数据
│   ├── insurance_products/
│   └── compliance_rules/
└── icon.png                       # 32x32图标(可选)
```

### manifest.json模板

```json
{
  "name": "insurance-sales-mcp",
  "version": "1.3.0",
  "description": "香港保险咨询销售MCP Server — GL-44/RL-010合规，11个工具：产品查询、合规检查、需求诊断、异议处理、SOP执行器、合规改写、生命周期分析、CRM标签、多轮对话、趋势分析、GL34合规",
  "icon": "icon.png",
  "author": "Insurance Tech Team",
  "license": "Apache-2.0",
  "manifest_version": "1.0",
  "protocol": "mcp",
  "server": {
    "command": "python3",
    "args": ["server.py"],
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  },
  "compliance": {
    "disclaimer": "本平台提供的信息仅供参考，不构成专业保险建议。如需正式投保咨询，请联系持牌保险中介人。",
    "data_privacy": "所有数据处理在本地进程完成。如连接云端模型，数据将传输至所选模型的API提供商。客户个人信息仅在用户明确同意后处理。",
    "target_audience": "香港居民（持牌保险中介人及其客户）",
    "regulatory_framework": ["GL-44", "GL34", "GN16", "RL-010"]
  },
  "tools": [
    {
      "name": "insurance_product_query",
      "description": "查询香港保险产品条款（list/detail，模糊匹配：危疾→重疾险）"
    },
    {
      "name": "compliance_check",
      "description": "GL-44/RL-002/RL-010等14条红线+4条黄线合规扫描"
    },
    {
      "name": "needs_assessment",
      "description": "客户需求诊断引擎（A/B/C/D分级）"
    },
    {
      "name": "objection_handler",
      "description": "6大类×3层级异议处理话术生成"
    },
    {
      "name": "private_sop_runner",
      "description": "私域Day-0~7 SOP全流程执行器"
    },
    {
      "name": "compliance_rewrite",
      "description": "违规内容自动改写引擎（前后对比+二次验证）"
    },
    {
      "name": "lifecycle_analyzer",
      "description": "D0→D30客户生命周期分析（5阶段模型）"
    },
    {
      "name": "client_crm_tag",
      "description": "CRM标签生成/查询/导出"
    },
    {
      "name": "multi_turn_dialogue",
      "description": "80轮会话上下文管理"
    },
    {
      "name": "compliance_trend_analysis",
      "description": "历史违规趋势分析+规则统计"
    },
    {
      "name": "gl34_compliance_check",
      "description": "GL34分红保单治理合规检查（6条规则）"
    }
  ]
}
```

### 打包脚本 (python packer.py)

```python
#!/usr/bin/env python3
"""将MCP Server打包为.mcpb Desktop Extension"""
import zipfile, json, os, pathlib

PROJECT_ROOT = pathlib.Path(__file__).parent
OUTPUT = "insurance-sales-mcp.mcpb"

def pack():
    manifest_path = PROJECT_ROOT / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 写入manifest（根目录）
        for entry in ["server.py"] + list((PROJECT_ROOT / "src").rglob("*")):
            if entry.is_file():
                arcname = str(entry.relative_to(PROJECT_ROOT))
                zf.write(entry, arcname)
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    print(f"✅ 打包完成: {OUTPUT}")
    print(f"📦 大小: {os.path.getsize(OUTPUT)} bytes")

if __name__ == "__main__":
    pack()
```

### 用户安装流程（.mcpb）

1. 下载 `insurance-sales-mcp.mcpb`
2. 双击 → 自动关联到Claude Desktop
3. Claude Desktop弹窗确认安装
4. ✅ 安装完成，MCP Server自动注册

---

## 三、方案B: stdio本地配置（开发者）

### claude_desktop_config.json

```json
{
  "mcpServers": {
    "insurance-sales": {
      "command": "python3",
      "args": ["/Users/charles/.openclaw/workspace/knowledge/sales-skills/mcp/src/server.py"],
      "env": {
        "SERVER_API_KEY": "",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Claude Desktop侧设置（Settings → Connectors）

如果Claude Desktop版本支持Connectors界面：
1. Settings → Connectors → Add custom connector
2. MCP Server名称: `insurance-sales`
3. Command: `python3 /path/to/src/server.py`
4. ✅ 保存并重启Claude Desktop

---

## 四、方案C: 第三方模型Gateway（Developer Mode，最新功能）

**适用**: Claude Desktop v4.0+ Developer Mode

### 配置路径
```
Help → Troubleshooting → Enable Developer Mode
Developer → Configure Third-Party Inference
```

### Gateway配置（直连我们的HTTP MCP Server）

```json
{
  "connection": {
    "type": "Gateway",
    "baseUrl": "https://your-server.example.com:18060/mcp/",
    "authScheme": "Bearer",
    "apiKey": "your-mcp-api-key"
  },
  "modelList": [
    "claude-sonnet-4-20250514",
    "deepseek-v4"
  ]
}
```

### ⚠️ 合规注意事项
- 第三方Gateway的API Key和请求会经过Gateway提供商服务器
- 建议仅使用香港/新加坡节点的可靠Gateway（如Glama Gateway）
- 客户个人信息输入需谨慎，避免在Gateway日志中留存

---

## 五、Claude Desktop扩展合规要求清单

### 首次安装弹窗内容（强制）

```
🛡️ 香港保险咨询销售 MCP Server — 合规声明

【免责声明】
本平台提供的信息仅供参考，不构成专业保险建议。
如需正式投保咨询，请联系持牌保险中介人。

【数据隐私】
• 所有数据处理在本地进程完成
• 仅在你主动调用工具时执行对应操作
• 如选择云端模型API，数据将传输至所选提供商
• 不会自动发送或存储你的个人信息

【目标用户】
本工具面向香港居民（持牌保险中介人及其客户）使用。

【监管框架】
本工具内置香港保监局GL-44、GL34、GN16合规检查规则。
```

---

## 六、下一步行动项

| # | 任务 | 负责 | 状态 |
|---|------|------|------|
| 1 | manifest.mcpb.json 更新（整合R55版本） | R56 | ⬜ |
| 2 | .mcpb packer.py 编写 | R56 | ⬜ |
| 3 | icon.png (32x32) 准备 | CJ | ❌ 阻塞 |
| 4 | 完整安装指南文档 | R56 | ⬜ |
| 5 | Glama提交（含.mcpb下载链接） | R57+ | ❌ GitHub repo前置 |

---

*本方案基于Anthropic官方文档 + Collabnix实测验证。*
*Claude Desktop Desktop Extensions格式：.mcpb (2025年9月从.dxt升级)*
