# Agentic 工作流设计 v2.2 (保险咨询与销售)
**创建时间**: 2026-06-16 | **最后更新**: 2026-06-17
**版本**: v2.2（R26升级）
**用途**: 保险咨询与销售全流程自动化引擎 + 多轮对话状态机 + 客户生命周期管理 + 会话管理层

---

## 架构概览 v2.0

```
用户输入 → [阶段1: 需求识别] → [阶段2: 方案匹配] → [阶段3: 合规校验] → [阶段4: CTA/转化]
               ↓                      ↓                    ↓                    ↓
          客户画像生成           产品矩阵推荐           红线扫描              CTA输出
          分级标签(A/B/C/D)      匹配理由说明           违规词拦截             私域路径
          风险偏好评估           替代方案提示           监管条款引用           SOP编排

[←←←←←←←←←←←←←←←←←←←←←←←←←] 多轮对话状态追踪层 [←←←←←←←←←←←←←←←←←←←←←←←←←]
```

### v2.2 vs v2.1 核心差异
| 维度 | v2.1 | v2.2（新增） |
|------|------|-------------|
| 会话管理 | 无独立管理层 | **SessionManager** — 内存+磁盘双层存储、80轮上下文窗口、自动摘要 |
| MCP集成 | 基础stdio | + **OpenAPI 3.1 spec** + session子协议 + HTTP端点 `/sessions` |
| CLI | v7.0 (23 cmds) | **v7.1** — 新增 `session-list`/`session-export-full`/`session-summarize` |
| 上下文窗口 | 10轮默认 | **80轮滑动窗口**（R26从10扩至80） |
| 合规记忆 | 基础禁令列表 | **增强型**：含auto_rewrite suggestions + violation trend |
| Agent Prompt模板 | 固定格式 | **动态上下文注入**（实时grade/intent/drift/compliance memory） |

---
| 维度 | v1.0 | v2.0（新增） |
|------|------|-------------|
| 对话管理 | 单轮无状态 | 多轮状态机 + 上下文记忆窗 |
| 需求追踪 | 每次独立检测 | 需求演化路径 + 优先级漂移检测 |
| 客户生命周期 | 无 | 完整D0→D7旅程 + 客户分级演化 |
| MCP集成 | 无 | 全部5个工具通过MCP Protocol暴露 |
| CLI v6.2 | — | 新增`mcp-server`/`mcp-call`命令 |
| 记忆管理 | — | 会话JSON持久化 + 自动摘要 |

---

## 🆕 Module B: 多轮对话状态机 (Multi-Turn Conversation State Machine)

### v2.1 改进（R24）
| 项目 | v2.0 | v2.1 |
|------|------|------|
| Grade升级逻辑 | 仅当health_concern+income_protection组合触发A级 | 新增: income_protection alone → B级, health+≥2信号→A级, urgent+任何需求→warm/urgent |
| Urgency评估 | 依赖显式紧急词列表 | 新增: 含'万一/出事/后果'自动升级urgent; 有明确需求但无紧急词→WARM |
| SOP Day推进 | B级客户在turn_count≥4时触发 | 改进为Grade A/B → sop_day=max(sop_day,3)即时推进 |

### 状态结构
```python
class DialogueStateV2:
    session_id: str                    # 唯一会话ID
    turn_count: int                    # 已处理轮次
    intent_current: str                # 当前意图类别（health/family/savings/travel/property/cross_border/objection/unclear）
    intent_history: List[IntentTurn]   # 意图演化路径（每轮记录）
    needs_evolved: List[NeedSignalV2]  # 需求演化列表（含优先级漂移）
    customer_grade_evolution: List[str]# 客户分级演化路径
    products_discussed: List[str]      # 已讨论的产品列表
    objections_raised: List[Objection] # 客户提出的异议类型
    compliance_flags: List[Violation]  # 历史违规标记（防止反复）
    context_window: List[TurnEntry]    # 最近N轮对话上下文（默认10轮）
    last_action: str                   # 最近agent行动建议
    sop_day: int = 0                   # 当前SOP天数
    sop_cta_count: int = 0             # CTA已触发次数
    customer_profile: dict             # 客户画像快照（动态更新）
    
class IntentTurn:
    turn: int
    intent: str
    confidence: float
    needs_extracted: List[str]

class NeedSignalV2(NeedSignal):
    need_type: str
    confidence: float
    keywords_matched: List[str]
    priority_weight: float = 0.0       # R19新增：需求权重评分
    detected_at_turn: int              # 首次检测轮次
    
class TurnEntry:
    turn: int
    role: str                          # "user" | "agent"
    content: str                       # 原文
    extracted_needs: List[str]         # 该轮提取的需求
    compliance_checked: bool           # 是否合规检查
```

### 意图演化引擎 (Intent Evolution)
```python
INTENT_CATEGORIES = {
    "health":     ["health_concern", "medical_need", "elderly_care"],
    "family":     ["income_protection", "family_responsibility"],
    "savings":    ["savings_plan"],
    "travel":     ["travel_fear"],
    "property":   ["property_risk"],
    "cross_border":["cross_border"],
    "objection":  ["price", "trust", "delay"],
    "unclear":    [],
}

def detect_intent_evolution(needs_list: List[NeedSignalV2]) -> tuple[str, float]:
    """从需求信号推断主意图 + 置信度"""
    if not needs_list:
        return ("unclear", 0.3)
    
    intent_map = {}
    for need in needs_list:
        for intent, types in INTENT_CATEGORIES.items():
            if need.need_type in types:
                intent_map[intent] = intent_map.get(intent, 0) + need.confidence
    
    if not intent_map:
        return ("unclear", 0.3)
    
    best_intent = max(intent_map, key=intent_map.get)
    confidence = min(0.95, intent_map[best_intent] / len(needs_list))
    return (best_intent, confidence)
```

### 需求优先级漂移检测 (Priority Drift Detection)
当客户需求在对话中发生显著变化时自动检测：
```python
def detect_priority_drift(evolved_needs: List[NeedSignalV2], threshold=0.15):
    """检测需求优先级是否发生重大变化"""
    if len(evolved_needs) < 2:
        return {"drift_detected": False}
    
    # 对比首次和最新Top需求
    first_top = evolved_needs[0]       # 按最早出现顺序
    latest_top = max(evolved_needs, key=lambda n: n.confidence)
    
    confidence_diff = abs(latest_top.confidence - first_top.confidence)
    need_type_changed = first_top.need_type != latest_top.need_type
    
    if need_type_changed and confidence_diff > threshold:
        return {
            "drift_detected": True,
            "drift_type": "primary_need_switch",
            "from_need": first_top.need_type,
            "to_need": latest_top.need_type,
            "confidence_change": round(confidence_diff, 2)
        }
    
    return {"drift_detected": False}
```

### 合规记忆机制 (Compliance Memory)
防止Agent在后续回复中重复触发相同的违规：
```python
def get_compliance_memory(flags: List[Violation], history_window=5):
    """从历史违规标记生成禁令清单，供后续回复参考"""
    recent = flags[-history_window:] if len(flags) > history_window else flags
    bans = set()
    for flag in recent:
        bans.add(flag.rule_id)
    return {
        "prohibited_rules": list(bans),
        "last_violation_at_turn": flags[-1].turn if flags else None,
        "auto_rewrites_needed": [f["suggestion"] for f in recent]
    }
```

### 完整状态机流转
```mermaid
stateDiagram-v2
    [*] --> Unidentified: 首次消息
    
    state Unidentified {
        [*] --> ExtractNeeds: 需求信号检测
        ExtractNeeds --> GradeCustomer: 客户分级
        GradeCustomer --> ReadyForFlow
    }
    
    ReadyForFlow --> NeedsConfirmed: A/B级 → 确认需求
    ReadyForFlow --> ContentNurture: C/D级 → 科普引导
    
    state NeedsConfirmed {
        [*] --> MatchSolutions: 方案匹配
        MatchSolutions --> ComplianceGate: 合规校验
        ComplianceGate --> Approved: PASS/FLAGGED(改写)
        ComplianceGate --> Blocked: BLOCKED
        Approved --> GenerateCTA: CTA生成
    }
    
    state ContentNurture {
        [*] --> EducateContent: 科普内容
        EducateContent --> ReassessGrade: 重新分级
        ReassessGrade --> NeedsConfirmed: 升级为A/B
        ReassessGrade --> ContentNurture: 保持C/D
    }
    
    state Blocked {
        [*] --> ComplianceExplanation: 合规解释话术
        ComplianceExplanation --> EducationalContent: 纯教育内容
        EducationalContent --> WaitForReply: 等待客户回复
    }
    
    GenerateCTA --> WaitForReply
    Blocked --> WaitForReply
    ContentNurture --> WaitForReply
    
    WaitForReply --> NeedsConfirmed: 客户明确需求
    WaitForReply --> ContentNurture: 客户犹豫/观望
    WaitForReply --> NeedsConfirmed: (后续轮次)
    
    state MultiTurnMemory {
        ContextWindow ← turn1 → turn2 → ... → turnN
        IntentEvolution tracks shifts
        PriorityDrift detects changes
    }
```

---

## 🆕 客户生命周期管理 (Customer Lifecycle Management)

### 五阶段模型
| 阶段 | 触发条件 | Agent动作 | SOP关联 |
|------|---------|----------|---------|
| **L1: Discovery** | 首次消息（D0） | welcome_message + needs_discovery | Day-0 |
| **L2: Qualification** | 需求确认（D1-D3） | content_nurture → grade评估 | Day-1/Day-3 |
| **L3: Solution Design** | A/B级客户（D4-D5） | solution_education + product框架 | Day-5 |
| **L4: Conversion** | 预约咨询触发（D6-D7） | cta_or_reactivate | Day-7 |
| **L5: Nurturing** | C/D级持续培育 | 内容+教育循环 | D1-D7循环 |

### 客户分级演化规则
```python
GRADE_EVOLUTION_RULES = {
    "D → C":  检测到2个以上风险信号且含明确需求词,
    "C → B":  客户主动提问产品相关/表达具体保障需求,
    "B → A":  同时表达医疗+收入/家庭双重需求 或 跨境身份+保障需求,
    "A 降级":  连续2轮无响应 + 超过48h未触达 → C级降档
}
```

---

## 🆕 MCP集成架构

### 工作流工具调用链（Agent视角）
```
User Message
    ↓
[Agent: needs_assessment]      ← MCP Tool #3 — 需求诊断
    ↓
[MCP returns: grade, urgency, detected_needs]
    ↓
If grade in [A, B]:
    [Agent: insurance_product_query(action=detail)]  ← MCP Tool #1
    [Agent: handle_objection(category, tier)]        ← MCP Tool #4 (如客户有异议)
Else:
    [Agent: private_sop_runner(action=cross-border-journey)]  ← MCP Tool #5
    ↓
[Agent: compliance_check(text=final_response)]     ← MCP Tool #2 — 合规门禁
    ↓
If PASS → Send to client
If BLOCKED → Auto-rewrite using compliance suggestions
```

### Agent内部Prompt模板 (v2.0)
```
你是一个香港保险咨询顾问。当前会话ID: {session_id}

【客户画像】
分级: {current_grade} | 紧迫度: {urgency} | 主意图: {current_intent}
需求信号: {detected_needs_summary}
需求演化: {needs_evolution_summary}
优先级漂移检测: {drift_status}

【合规记忆】（最近5轮违规记录）
禁止规则: {prohibited_rules}
自动改写建议: {auto_rewrites}

【当前阶段】{current_lifecycle_stage}

请严格按以下步骤处理：
1. 调用 needs_assessment MCP工具（如有新消息输入）
2. Grade A/B → 调用 insurance_product_query MCP工具查询产品框架
3. 生成回复前，必须调用 compliance_check MCP工具做最终合规校验
4. 如通过 → 输出CTA；如BLOCKED → 用auto_rewrite建议生成替代回复
5. 更新对话状态机（记录本轮意图、需求、合规结果）

【约束】
- 严禁重复触发禁止规则中的任何违规行为
- Grade C/D不得直接推荐产品，必须走SOP内容培育流程
- 所有CTA必须包含"无推销压力"声明
- 输出格式：JSON{analysis, recommendation, compliance_check_result, cta_output}
```

---

## CLI v6.2 新增命令

### `mcp-server` — 启动MCP Server
```bash
python insurance-sales-cli.py mcp-server --start     # 后台启动
python insurance-sales-cli.py mcp-server --status    # 查看状态
python insurance-sales-cli.py mcp-server --stop      # 停止
```

### `mcp-call` — CLI直接调用MCP工具（无需HTTP/stdio交互）
```bash
# 内部封装，直接调用server.py中的工具函数
python insurance-sales-cli.py mcp-call tool:needs_assessment --message "我想给家人留保障"
python insurance-sales-cli.py mcp-call tool:compliance_check --text "这款产品价格合适"
```

### `workflow-v2` — 完整多轮工作流（含状态追踪）
```bash
# 初始化会话
python insurance-sales-cli.py workflow-v2 init --session s01

# 第一轮对话
python insurance-sales-cli.py workflow-v2 next --sid s01 --message "我有房贷要还"

# 第二轮对话（自动继承上下文）
python insurance-sales-cli.py workflow-v2 next --sid s01 --message "最近体检发现结节"

# 查询会话状态
python insurance-sales-cli.py workflow-v2 state --sid s01

# 导出完整分析
python insurance-sales-cli.py workflow-v2 export --sid s01
```

---

## 完整执行示例

### 场景：多轮客户对话（5轮）

**Round 1**: "我想给家人留点保障"
- Grade: D → C (检测到家庭责任+收入保护)
- Action: content_nurture (科普引导)
- SOP: Day-0 welcome + Day-1 GN16教育

**Round 2**: "我有房贷要还，万一出事家里怎么办？"
- Grade: B → A (收入保障+家庭责任双重信号)
- Intent drift: unclear → family (confidence 0.85)
- Action: insurance_product_query (定期寿险框架)
- Compliance: PASS

**Round 3**: "保费太贵了，有没有便宜点的？"
- Objection detected: price category
- Grade: A (需求未变但出现价格异议)
- Action: handle_objection(category=price, tier=medium) + product_query(对比方案)
- Compliance: PASS (异议话术合规)

**Round 4**: "好的，那我什么时候可以预约咨询？"
- Conversion signal detected!
- Grade: A
- Action: cta_or_reactivate (Day-7 CTA)
- SOP: Day-3/Day-5触达 + Day-7预约

**Round 5**: "我下周三是可以的"
- Appointment confirmed!
- Action: schedule_confirmed
- Grade: A (已转化)
- SOP: 预约提醒 + 资料准备

---

## v2.1 工具生态扩展

| 模块 | 文件 | 功能 |
|------|------|------|
| MCP Server | `mcp/server.py` | 5个工具, stdio/HTTP双协议 |
| HTTP Server | `mcp/server_http.py` | HTTP传输模式（端口18060） |
| Test Suite | `mcp/test_mcp_suite.py` | 21项测试（16HTTP+5stdio） |
| OpenAI Adapter | `mcp/openai_schema_adapter.py` | [v2.1新增] OpenAI function calling schema转换 |
| Gemini Config | `mcp/gemini_config_generator.py` | [v2.1新增] Google AI Studio/Gemini CLI配置生成 |
| CLI Tools | `cli/insurance-sales-cli.py` | v7.0, 23个命令 |
| Workflow v2 | `cli/AGENTIC-WORKFLOW-DESIGN.md` | 多轮状态机+生命周期管理 |

## v2.1 文件变更清单（本轮）

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `AGENTIC-WORKFLOW-DESIGN.md` | **升级** | v1.0 → v2.0：多轮状态机+客户生命周期+MCP集成架构 |
| `mcp/server.py` | **新增** | MCP Server (Module A) — 5个工具, stdio协议 |
| `insurance-sales-cli.py` | **扩展** | v6.1 → v6.2：+mcp-server/+mcp-call/+workflow-v2 新命令 |
| `cli/AGENTIC-WORKFLOW-DESIGN.md` | **升级** | 同左，复制到cli目录保持兼容 |

## v2.1 文件变更清单（本轮）

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `cli/AGENTIC-WWORK-DESIGN.md` | **升级** | v2.0 → v2.1: Grade/Urgency逻辑增强 |
| `mcp/openai_schema_adapter.py` | **新增** | OpenAI function calling schema适配器 |
| `mcp/gemini_config_generator.py` | **新增** | Gemini CLI / Google AI Studio配置生成器 |

---

## 🆕 Module A.5: Session Management (R26新增)

### SessionManager API
```python
from mcp.session_manager import SessionManager, DialogueSession

manager = SessionManager()

# CRUD operations
session = manager.create_session("s001")         # Create
session = manager.get_session("s001")             # Read (auto-persist)
session = manager.add_turn_to_session(s001, data)  # Update
sessions = manager.list_sessions(limit=50)         # List
summary = manager.summarize_session("s001")        # Quick browse
data = manager.export_session("s001")             # Full JSON export
manager.delete_session("s001")                     # Delete
```

### 状态机集成
```python
# Each turn auto-updates:
session.add_turn({"role":"user", "content":msg, 
                  "extracted_needs":[...], "grade":"B",
                  "compliance_result":{...}})

# State machine queries
intent = session.detect_intent_evolution()     # {current_intent: 'family', confidence: 0.56}
drift  = session.detect_priority_drift()        # {drift_detected: False}
comp_mem = session.get_compliance_memory()      # {prohibited_rules: [...], total_violations: 0}
```

### 持久化机制
- **内存缓存**: active sessions 保留在 RAM（`_cache` dict）
- **磁盘存储**: 每次 create/update 自动写入 `cli/sessions/{session_id}.json`
- **加载策略**: get_session 优先缓存，缓存未命中则从磁盘反序列化
- **格式兼容**: JSON结构完全对齐 AGENTIC-WORKFLOW-DESIGN.md v2.1 DialogueStateV2 schema

---

## 🆕 CLI v7.1 新增命令 (R26)

### `session-list` — 列出所有会话记录
```bash
python insurance-sales-cli.py session-list                    # 默认50条
python insurance-sales-cli.py session-list --limit 20         # 自定义限制
python insurance-sales-cli.py session-list --grade A          # 仅A级客户
```

### `session-export-full` — 导出完整会话（含上下文）
```bash
python insurance-sales-cli.py session-export-full s001 > s001.json
# 输出: 完整JSON含所有轮次、需求演化、合规记录
```

### `session-summarize` — 快速浏览会话摘要
```bash
python insurance-sales-cli.py session-summarize s001
# 输出:
#   Session s001: 5 turns, grade B, intent family (0.72)
#   Grade history: [D → B]
#   Products discussed: [定期寿险]
#   Compliance violations: 0
```

### `session-delete` — 清理会话
```bash
python insurance-sales-cli.py session-delete s001
```

---

## v2.2 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `AGENTIC-WORKFLOW-DESIGN.md` | **升级** | v2.1 → v2.2: 新增Session Management模块、CLI v7.1命令 |
| `mcp/OPENAPI.json` | **新增** | OpenAPI 3.1 spec — 9 endpoints, 16 schema types |
| `mcp/session_manager.py` | **新增** | SessionManager + DialogueSession (R26核心新增) |
| `insurance-sales-cli.py` | **扩展** | v7.0 → v7.1: +session-list/+session-export-full/+session-summarize/+session-delete |

---

## 后续迭代方向（v2.3+）
- [ ] Dify connector (自托管集成)
- [ ] GitHub repo + PyPI packaging
- [ ] Discord/Telegram bot bridge
- [ ] Customer CRM tag sync API
- [ ] A/B testing framework integration into MCP Tool
- [ ] Cantonese/Mandarin auto-switch improvement
