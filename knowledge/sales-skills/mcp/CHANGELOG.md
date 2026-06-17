# Changelog

All notable changes to the **Insurance Sales Advisory MCP Server** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

### Changed

### Fixed

### Security

---

## [1.0.0] — 2026-06-17 (R31)

### 🎉 MCP Server v2.0 Complete — 10 Tools, Platform-ready Release

#### Added — New Tools (5 new tools bringing total to 10)

- **`compliance_rewrite`** (Tool #6): Auto-fix violations → compliant text with before/after comparison + re-verification. Supports targeted rule fixes and auto-detection of all red-line rules. Covers 8 of 10 red-line rules via `COMPLIANCE_REWRITE_DB`.
- **`lifecycle_analyzer`** (Tool #7): D0→D30 customer lifecycle stage analysis with optimization pipeline. 5 stages (认知/信任/方案/决策/转化) with KPI targets, content strategy recommendations, and engagement-based priority matrix.
- **`client_crm_tag`** (Tool #8): Multi-dimension CRM tagging system. Auto-generates risk_profile, purchase_intent, compliance_flag, lifecycle_stage, and communication_pref tags from needs_assessment + engagement_score inputs. In-process demo DB (`DEMO_CRM_DB`) for query/export/categorize operations.
- **`multi_turn_dialogue`** (Tool #9): Session-level state machine for multi-turn dialogue management in stdio mode. Sliding context window (80 turns), grade evolution tracking, compliance flag accumulation, and summary generation. Eliminates external `session_manager.py` dependency for stdio mode.
- **`compliance_trend_analysis`** (Tool #10): Historical violation trend analysis engine. Per-rule statistics, risk level assessment, blocked/flagged rate computation, and policy update recommendations based on frequency thresholds.

#### Architecture Changes

- **Server version**: v1.0.0 → **v1.1.0** (MCP v2.0)
- **MCP_TOOLS schema**: 5 tools → **10 tools** with full JSON Schema definitions
- **TOOL_HANDLERS**: 5 handlers → **10 handlers** (complete coverage)
- **Internal state layer**: New `_SessionStore` class for in-process session memory + compliance history across all tools
- **Compliance rewrite mappings**: Added `COMPLIANCE_REWRITE_DB` with rule-to-compliant-alternative mappings for RL-001, RL-002, RL-003, RL-004, RL-005, RL-007, RL-008, RL-009
- **Lifecycle stage model**: Added `LIFECYCLE_STAGES` dict with 5 stages, KPI targets, content types, and compliance levels
- **CRM tag taxonomy**: Added `CRM_TAG_CATEGORIES` dict with 5 dimensions and auto-generation logic

#### Compliance Updates

- Red line rules: 10 RL-rules + RL-011 strict mode for hidden compliance violations
- Yellow line rules: 4 YL-rules operational across all tools
- GL-44 cross-border coverage fully mapped (all regulatory refs in `REGULATORY_REFS`)
- Auto-rewrite capability covers 8 of 10 red-line rules (RL-006 excluded — requires manual handling due to product name + amount combo complexity)

#### Documentation

- **CHANGELOG.md**: This file — full history from R26→R31
- **LICENSE**: Apache-2.0 full text included
- **README-developer.md** → extended as developer guide with architecture diagrams
- **README-marketing-developer.md**: GitHub release marketing README (new)

#### Packaging & Distribution

- `pyproject.toml`: Updated version to `1.0.0`, expanded description for 10 tools
- `setup.py`: Legacy packaging support maintained
- **Dockerfile-mcp**: Verifies all source files copied; CMD defaults to `server_http_r27.py`
- **docker-compose.yml**: Volume mounts for sessions directory sharing between CLI and MCP container

#### Testing

- All 10 tools functional in stdio JSON-RPC mode (verified via `test_mcp_suite.py`)
- HTTP REST API: Session CRUD endpoints (6 endpoints) on port 18060
- KB Validator: product DB (14 products, 100% field completeness), objection DB (68 scenarios), compliance rules (14 red + 4 yellow lines)

---

## [0.1.0] — 2026-06-17 (R26 → R29)

### 📦 Initial v2.0 Foundation — Core MCP Server Released

#### Added (R26 — Session Management + OpenAPI Spec)

- **`session_manager.py`**: Full multi-turn dialogue state machine
  - `DialogueSession` with 80-round sliding context window
  - Intent evolution engine (auto-detect primary intent + confidence)
  - Priority drift detection (auto-identify client need changes)
  - Compliance memory system (violation ban list + auto_rewrite suggestions)
  - Memory + disk dual-layer persistence (`cli/sessions/` directory)
  - CRUD API: create/get/add_turn/list/export/delete/summarize

- **`OPENAPI.json`** (16.9KB): OpenAPI 3.1.0 compliant spec
  - 9 endpoints, 16 schema types
  - Full parameter documentation for 5 original MCP tools

- **`kb_validator.py`** (8.8KB): Knowledge base integrity validator
  - Product DB: 14 products, 100% field completeness check
  - Objection DB: 68 scenarios across 6 categories × 3 tiers
  - Compliance rules: 10 red lines + 4 yellow lines verification

- **`AGENTIC-WORKFLOW-DESIGN-R26.md`**: Agentic workflow design v2.2 specification

#### Added (R27 — HTTP Session CRUD + CLI v7.1)

- **`server_http_r27.py`** (300 lines): Session CRUD REST API with MCP JSON-RPC compatibility
  - `POST /sessions/create` — Create new session (auto-assign sid)
  - `GET /sessions/list?limit=N` — List sessions sorted by update time
  - `GET /sessions/<sid>` — Export full session JSON
  - `GET /sessions/summarize?sid=X` — Generate summary (intent + drift + compliance memory)
  - `POST /sessions/<sid>/add-turn` — Add turn with auto needs_analysis + compliance_check
  - `POST /sessions/<sid>/delete` — Delete session

- **CLI v7.1**: 6 new session commands (`session-create/add-turn/list/export-full/summarize/delete`)
- **Docker Compose update**: Added sessions directory volume mount for CLI-container sharing

#### Fixed (R27)

- **Session persistence across processes** (HIGH severity): Fixed field name mismatch between `to_dict()` and `get_session()` for `needs_evolved` list serialization
- **HTTP GET route ordering** (MEDIUM severity): Moved specific routes before catch-all to prevent `/sessions/summarize` being matched by `/sessions/<sid>` pattern

#### Added (R28) — Platform Inventory Complete

- Full inventory of 10 target platforms assessed
- Compliance evaluation matrix across all platforms (Claude Desktop, Cursor/Windsurf, OpenAI, LangChain, Dify, n8n, Coze, WeChat Mini Program, Discord/Telegram bot)

#### Added (R29) — Platformization Phase

- **`R29-DIFY-INTEGRATION-PLAN.md`**: Complete Dify bidirectional MCP integration architecture
  - Data flow diagram: Dify App → MCP SSE → our Server → KB/RL rules
  - Docker Compose deployment for Dify + Insurance MCP
  - Compliance analysis: data export=NONE, PII=MEDIUM, GL-44=COMPLIANT

- **Python packaging** (`setup.py` + `pyproject.toml`): PyPI-ready packaging
  - Package name: `insurance-sales-mcp` (v0.1.0)
  - Dependencies: httpx, sse-starlette, pydantic
  - Entry point: `insurance-mcp` CLI command

- **`README.md`**: Initial quick-start documentation (stdio/HTTP/Docker three ways)

#### Platform Integration Status (as of R29)

| Platform | MCP Support | Status |
|----------|------------|--------|
| Claude Desktop | stdio | ✅ Connected |
| Cursor/Windsurf | stdio | ✅ Connected |
| OpenAI Responses API | tool_format | ⏸️ Pending v2.0 schema compatibility |
| LangChain/LangGraph | MCP SDK | ⏸️ Pending |
| Dify | SSE + MCP bridge | ✅ Plan complete |
| n8n | — | ⏸️ P2 priority |
| Coze/扣子 | — | 🔴 BLOCKED (compliance review required) |

---

## [0.0.x] — Early Rounds (Pre-R26)

The project originated from insurance sales skill iteration workflows. Pre-R26 development included:

- Initial MCP server prototype with core 5 tools
- CLI v6.0 → v7.0 iterative upgrades (12 → 23 commands)
- Product clauses database (14 products)
- Objection scripts database (68 scenarios × 3 tiers)
- Red-line rule set: RL-001 ~ RL-010
- Yellow-line rule set: YL-001 ~ YL-005

---

## Version History Summary

| Version | Round(s) | Date | Tools | Key Milestone |
|---------|----------|------|-------|---------------|
| 0.0.x | Early | Pre-Jun 2026 | 3 → 5 | MCP prototype + CLI foundation |
| 0.1.0 | R26–R29 | Jun 17, 2026 | 5 | Session management, OpenAPI spec, HTTP CRUD, platformization |
| **1.0.0** | **R30–R31** | **Jun 17, 2026** | **10** | **MCP v2.0 — full toolset, compliance architecture, release-ready** |

---

## Compliance Evolution

| Round | Red Lines | Yellow Lines | New Compliance Feature |
|-------|-----------|-------------|----------------------|
| Early | RL-001–RL-005 | YL-001–YL-003 | Basic scanning |
| R26 | RL-001–RL-010 | YL-001–YL-005 | Rule library complete + KB validator |
| R30 | RL-001–RL-010 + RL-011 (strict) | YL-001–YL-005 | Auto-rewrite DB (8 rules) + compliance trend analysis |

---

## Notes

- **RL-006** exclusion: Requires manual handling because it involves product name + amount combinations which need contextual awareness beyond regex patterns.
- **RL-011** (strict mode): Detects implicit yield promises (e.g., "投资回报", "资产增值") not covered by standard red-line rules.
- All compliance data operates on local-only storage; no PII is transmitted externally.
- GL-44 cross-border red lines (RL-010) are enforced at every tool output layer.
