# R44: MCPB (MCP Bundles) 打包实施方案

**时间**: 2026-06-18 01:05 HKT  
**来源**: Anthropic官方 @anthropic-ai/mcpb v2.1.2 npm包（已确认发布6个月）

---

## 📋 什么是 .mcpb

MCP Bundles (.mcpb) 是Anthropic官方的本地MCP服务器分发格式：
- **本质**：zip归档 + manifest.json描述文件
- **类比**：Chrome扩展(.crx) / VS Code扩展(.vsix)
- **目的**：一键安装本地MCP Server到Claude Desktop/Cursor等桌面AI应用
- **优势**：自动更新、配置变量管理、审核目录

## 🛠 打包步骤

### Step 1: 准备服务器文件结构
```
insurance-sales-mcp/
├── server.py              # MCP Server主入口
├── session_manager.py     # 会话管理
├── kb_validator.py        # 知识库验证
├── src/tools/             # 所有工具模块 (12个.py)
├── knowledge/             # 知识库数据
│   ├── insurance_products.json
│   ├── compliance_rules.json
│   └── ...
├── OPENAPI.json           # OpenAPI规范
├── requirements.txt       # Python依赖
└── README.md              # 使用说明
```

### Step 2: 创建manifest.json
```json
{
  "name": "insurance-sales-mcp",
  "version": "1.0.0",
  "description": "香港保险私域获客MCP Server — 11个工具完整合规引擎",
  "manifestVersion": 1,
  "tools": [
    {
      "name": "insurance_product_query",
      "description": "香港保险产品查询（list + detail，支持模糊匹配）"
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
      "description": "6大类×3层级异议处理话术"
    },
    {
      "name": "private_sop_runner",
      "description": "私域Day-0~7 SOP全流程执行器"
    }
  ],
  "transport": "stdio",
  "command": "python3",
  "args": ["server.py"],
  "variables": [
    {
      "name": "KB_PATH",
      "description": "知识库目录路径",
      "required": true,
      "default": "${workspaceFolder}/knowledge"
    },
    {
      "name": "SERVER_API_KEY",
      "description": "API访问密钥（用于HTTP模式）",
      "required": false
    }
  ],
  "platforms": ["darwin", "linux", "win32"],
  "author": "Clawsure Team",
  "license": "Apache-2.0"
}
```

### Step 3: 创建打包脚本
```bash
#!/bin/bash
# pack-mcpb.sh — 一键生成 .mcpb bundle
set -euo pipefail

PKG_NAME="insurance-sales-mcp-1.0.0.mcpb"
BUILD_DIR=$(mktemp -d)

# 复制文件到构建目录
cp -r knowledge/ "$BUILD_DIR/"
cp server.py session_manager.py kb_validator.py OPENAPI.json README.md "$BUILD_DIR/"
cp -r src/tools/ "$BUILD_DIR/"

# 创建manifest.json（动态版本）
cat > "$BUILD_DIR/manifest.json" << 'EOF'
{上述manifest内容}
EOF

# 生成mcpb bundle (zip with manifest)
cd "$BUILD_DIR"
zip -r "../$PKG_NAME" . -x "*.git*" ".__*"
cd -

echo "✅ Bundle created: $PKG_NAME ($(du -h $PKG_NAME | cut -f1))"
rm -rf "$BUILD_DIR"
```

### Step 4: 安装到Claude Desktop（手动）
1. Claude Desktop → Settings → Developer Tools → Edit Config
2. 添加 .mcpb 路径指向生成的文件
3. 或双击 .mcpb 文件（macOS自动处理）

## 📊 分发渠道优先级

| 渠道 | 优先级 | 实施状态 | 合规风险 |
|------|--------|---------|---------|
| GitHub Releases (zip+mcpb) | P0 | 待GitHub repo | 🟢 LOW |
| Smithery (npm包) | P1 | setup.py已就绪 | 🟢 LOW |
| Glama Registry | P1 | manifest.json模板就绪 | 🟡 MEDIUM |
| .mcpb官网发布（anthropic） | P2 | 待审核目录 | 🟢 LOW |
| 直接分享（用户本地安装） | P0 | 可立即执行 | 🟢 NONE |

## 🔒 合规检查清单

- [x] server.py不包含任何云端API调用（纯本地）
- [x] 知识库数据全量本地化，不上传第三方
- [x] compliance_check引擎在用户本地执行GL-44规则
- [ ] manifest.json需移除"香港保险"相关营销文字 → 改为技术描述
- [x] 无PII外泄路径（session数据TTL过期自动清理）
- [ ] 最终manifest提交前需合规终审

## R45行动项
1. 生成manifest.json模板文件
2. 编写pack-mcpb.sh打包脚本
3. 准备GitHub README中的MCPB安装章节
4. 提交CJ进行合规终审
