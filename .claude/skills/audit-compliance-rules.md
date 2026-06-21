# audit-compliance-rules — Review & Update Compliance Ruleset

## Description
Audits the compliance rule engine and recommends updates to thresholds, flags, and risk scoring logic.

## What It Does
1. Reviews current compliance scoring matrix in `tools/mocks.py`
2. Analyzes rule effectiveness by running test scenarios
3. Identifies gaps (e.g., missing PEP detection, outdated thresholds)
4. Recommends updates to risk categories or weighted factors
5. Documents changes for audit trail

## Usage
When you want to:
- Review compliance rule effectiveness
- Update risk thresholds based on business changes
- Add new compliance checks (e.g., FATCA, new jurisdiction rules)
- Audit compliance agent decisions for consistency

## Example Recommendations
```
Current rule: income > $1M → +15 risk points
Recommendation: Split into tiers:
  - $1M-$5M → +10 points
  - $5M+ → +20 points
  (Rationale: Ultra-high-net-worth clients require enhanced scrutiny)

Current: No FATCA check
Recommendation: Add FATCA indicator for US non-resident accounts
  (Rationale: Regulatory requirement for US persons abroad)
```

## Files Modified
- `tools/mocks.py:COMPLIANCE_RULES` — Risk scoring thresholds
- `agents/compliance_agent.py` — If new checks needed
- `COMPLIANCE_RULES.md` — Documentation (create if absent)

## Testing
After updates, run:
```bash
python main.py --sample-clients
```
Verify:
- High-net-worth clients (>$5M) properly categorized
- Sanctions matches still block immediately
- Risk scores are reasonable and consistent

## Audit Trail
All changes logged in `COMPLIANCE_AUDIT.md`:
- What was changed
- Why (business rationale)
- When (timestamp)
- Impact on sample clients

## See Also
- ARCHITECTURE.md — Compliance Agent design
- agents/compliance_agent.py — Agent implementation
- tools/mocks.py — Mock compliance data
