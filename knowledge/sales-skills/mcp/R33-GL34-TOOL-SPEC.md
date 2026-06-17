# GL34 Compliance Check Tool v2 — Specification (R33)

## Background
GL34 (修订版指引34《分红业务管治指引》) effective 2026-03-31, Section 4 company policy by 2026-06-30. This adds a 7th MCP tool: `gl34_compliance_check`.

## Tool Definition
```json
{
  "name": "gl34_compliance_check",
  "description": "Check insurance content against GL34 (Guideline 34) participating policy governance rules effective 2026-03-31 + Section 4 company policy by 2026-06-30. Returns compliance status with specific remediation suggestions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Insurance content text to check against GL34 rules"
      },
      "check_type": {
        "type": "string",
        "enum": ["all", "pbc_structure", "fund_isolation", "surplus_distribution", "disclosure_quality", "claim_ratio_accuracy"],
        "description": "Specific GL34 aspect to check. 'all' checks all 6 rule sets."
      },
      "policy_type": {
        "type": "string",
        "enum": ["participating", "savings", "critical_illness", "life"],
        "description": "Type of insurance policy being evaluated"
      }
    },
    "required": ["content"]
  }
}
```

## GL34 Rule Set (6 rules)

### GL34-001: Participating Policy Committee (PBC) Structure Check
**Trigger**: Content mentions participating policies or分红保险
**Rule**: Verify content acknowledges independent PBC oversight requirement
**Red line**: Cannot suggest policy benefits without acknowledging regulatory governance framework
**Severity**: RED_LINE if omitted in marketing materials

### GL34-002: Fund Asset Isolation Verification
**Trigger**: Content discusses fund performance, dividend distribution
**Rule**: Must state that participating funds are separately managed from shareholder assets
**Yellow line**: Missing isolation statement when discussing returns
**Severity**: YELLOW_LINE for incomplete disclosure

### GL34-003: Surplus Distribution Fairness
**Trigger**: Any content referencing expected returns, projected dividends
**Rule**: Returns must acknowledge fairness principle between policyholders and shareholders
**Red line**: Suggesting shareholder priority in surplus distribution
**Severity**: RED_LINE

### GL34-004: Disclosure Quality (GN16-rev alignment)
**Trigger**: Content contains financial figures or projections
**Rule**: Must clearly separate guaranteed vs non-guaranteed benefits; no "预期收益""预估分红" ambiguous terms
**Red line**: Using guaranteed language for non-guaranteed returns
**Yellow line**: Ambiguous return terminology
**Severity**: RED_LINE / YELLOW_LINE

### GL34-005: Claim Ratio Accuracy
**Trigger**: Content references company claim ratio or fulfillment ratio
**Rule**: Must cite specific date range, acknowledge 30-year history requirement per GN16-rev
**Yellow line**: Using outdated or unverified claim ratio data
**Severity**: YELLOW_LINE

### GL34-006: Illustration Rate Compliance (Dynamic)
**Trigger**: Content contains interest rate illustrations
**Rule**: Must not exceed current upper bound (HKD 6%, non-HKD 6.5% as of 2025-07-01; watch for 2026 revision to ~5%/5.5%)
**Red line**: Exceeding current regulatory cap
**Severity**: RED_LINE

## Implementation Notes
- Rules must be loaded from configuration file (not hardcoded) to support dynamic updates
- GL34 demonstration rate upper bound must be configurable via env var `GL34_ILLUSTRATION_HKD_RATE` and `GL34_ILLUSTRATION_NONHKD_RATE`
- When 保监局 announces rate cap revision, update takes effect within 1 config change (no code deploy needed)

## Integration with Existing System
This tool extends the existing `compliance_check` tool which currently has 10 RL + 4 YL rules. GL34 adds 6 additional rules that run in parallel during any compliance assessment.

### Updated Rule Library Structure:
```
Rule Category | Count | Coverage
RL-001~RL-010 | 10 | Core red lines (收益承诺, 保本保息, etc.)
YL-001~YL-005 | 5 | Yellow lines (绝对化用语, missing risk, etc.)
GL34-001~GL34-006 | 6 | GL34分红治理 rules
NEW-001~NEW-002 | 2 | Commission split / naming rules (future)
TOTAL | 23 | Comprehensive coverage
```

## Testing Requirements
1. Pass: Content mentioning PBC governance → no violation
2. Pass: Content without fund isolation statement when discussing returns → yellow_line GL34-002
3. Pass: Content with guaranteed language for non-guaranteed returns → red_line GL34-004
4. Pass: Content exceeding demonstration rate cap → red_line GL34-006
