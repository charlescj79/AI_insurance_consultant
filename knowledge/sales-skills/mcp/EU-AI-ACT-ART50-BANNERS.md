# EU AI Act Article 50 Compliance — Insurance MCP Banner Templates

**生成日期**: 2026-06-21 (R106)  
**法律依据**: Regulation (EU) 2024/1689, Article 50 - Transparency Obligations  
**生效日**: 2026-08-02 (⚠️ 41天倒计时)

---

## Art.50(1) Chatbot Disclosure — Required Text

### English (Minimum Requirement)
> "You are interacting with an AI insurance advisor. This service uses automated AI to provide general insurance information for reference only, and does not constitute professional financial or insurance advice. Results may contain errors."

### Chinese (Traditional - Primary HK Market)
> "您正在與AI保險顧問互動。此服務使用自動化人工智能提供一般保險資訊供參考，不構成專業金融或保險建議。結果可能包含錯誤。"

### Chinese (Simplified)
> "您正在与AI保险顾问互动。此服务使用自动化人工智能提供一般保险信息供参考，不构成专业金融或保险建议。结果可能包含错误。"

---

## Art.50(2) Synthetic Content Marking — Machine-Readable Tags

Our MCP outputs should include these metadata fields:

```json
{
  "_meta": {
    "generated_by": "insurance-sales-mcp v1.3.0",
    "ai_generated": true,
    "ai_act_compliant": true,
    "art50_reference": "Regulation (EU) 2024/1689 Article 50(2)",
    "c2pa_ready": false,
    "timestamp": "ISO-8601",
    "purpose": "reference_only"
  }
}
```

---

## Platform-Specific Deployment Instructions

### Dify Integration
- In Dify Agent workflow: add a system prompt node at the beginning with Art.50 disclosure text
- Compliance check node MUST precede all output nodes

### Telegram Bot
- Bot welcome message includes Art.50 disclosure banner
- Each AI response appended with "⚠️ AI-generated, for reference only"

### Discord Bot
- Channel description: "AI Insurance Advisor (Art.50 Compliant)"  
- First message on bot join: full disclosure banner

### 微信小程序
- 小程序页面底部显示："本内容由AI生成，仅供参考，不构成保险建议"
- 每次AI回复后附加免责声明

### Glama/LobeHub/mcp.so Directory Submissions
- server-card.json description includes EU AI Act Art.50 declaration (already done ✅)
- README.md includes dedicated compliance section (⚠️ needs update)

---

## Checklist Before Aug 2, 2026

- [x] server-card.json description含Art.50声明
- [ ] README.md增加EU AI Act合规章节 + Disclosure Banner模板
- [ ] PRIVACY_POLICY.md更新(含AI数据处理说明)
- [ ] Dify部署中配置compliance_check前置节点
- [ ] 所有前端平台首条消息显示Disclosure Banner
- [ ] CLI输出增加_meta meta字段 (C2PA-ready标记)
- [ ] 测试各平台的披露显示效果

---

_Penalty risk: up to €15M or 3% of global turnover for non-compliance_  
_Source: Bratby Law, artificialintelligenceact.eu, EU AI Act Service Desk_
