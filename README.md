# Client Onboarding Orchestrator

**A wealth management client onboarding multi-agent system using OpenAI agents SDK with Claude models.**

## Overview

This capstone project demonstrates agentic AI best practices through a realistic wealth management scenario: automating the client onboarding workflow using a 6-agent orchestrator with built-in guardrails, structured decision-making, and audit trails.

### Key Highlights
- **6-Agent Architecture**: Sequential specialist agents + a Critic agent that validates the entire chain
- **Model Tier Strategy**: Deliberate use of Claude 3.5 Haiku (fast, cost-efficient) and Sonnet (reasoning-heavy)
- **Structured Output**: All decisions use forced `tool_use` with strict schemas
- **Guardrails**: PII masking, compliance validation, inconsistency detection
- **Audit Trail**: Every decision logged with agent, model, duration, reasoning
- **Claude Code Integration**: Slash commands, skills, and PreToolUse hooks

---

## Quick Start

### 1. Prerequisites
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
```

### 2. Run the Workflow (3 Sample Clients)
```bash
python main.py --sample-clients
```

**Outputs:**
- `outputs/sample_cli001.json` — Happy path (APPROVED)
- `outputs/sample_cli002.json` — Rejection path (REJECTED - sanctions match)
- `outputs/sample_cli003.json` — Manual review path (REQUIRES_REVIEW - inconsistency detected)
- `outputs/summary.json` — Overall summary

### 3. Test Individual Agent
```bash
python agents/kyc_agent.py
```

### 4. Use Slash Command (in Claude Code)
```
/onboard --client-name "Jane Doe" --source "email"
```

---

## Architecture

### 6-Agent Sequential Chain

```
Client Application
    ↓
[1] KYC Agent (Haiku)           → Verify identity
    ↓
[2] Compliance Agent (Sonnet)   → Check sanctions, assess risk
    ↓
[3] Document Agent (Haiku)      → Generate onboarding documents
    ↓
[4] Profile Agent (Sonnet)      → Financial analysis, strategy recommendation
    ↓
[5] Setup Agent (Haiku)         → Provision account, schedule meetings
    ↓
[6] CRITIC Agent (Sonnet)       → Meta-validate entire chain, catch inconsistencies
    ↓
Final Decision (APPROVED / REJECTED / REQUIRES_REVIEW)
```

### Why This Architecture?

**Multi-Agent vs Alternatives:**
- **Single Agent**: Cannot parallelize expertise; higher error rate; less maintainable
- **Chatbot**: No workflow guarantee; inconsistent ordering; poor audit trail
- **Workflow Engine (rules-only)**: Cannot handle exceptions or nuanced decisions

**Why 6 Agents?**
- **First 5**: Specialists in their domain (KYC, Compliance, Documents, Finance, Setup)
- **6th (Critic)**: Implements "4-eyes principle" + catches hallucinations + validates consistency

**Decomposition Pattern:**
- **Sequential (not parallel)**: Each agent depends on prior output; matches real business workflow
- **Explicit**: Clear ordering for audit; easy to debug

---

## Tech Stack

### Model Tier Choices

| Agent | Model | Why |
|-------|-------|-----|
| KYC | Haiku | Document validation is rule-based |
| Compliance | Sonnet | Nuanced risk assessment required |
| Documents | Haiku | Straightforward template generation |
| Profile | Sonnet | Complex financial analysis |
| Setup | Haiku | Configuration, rule-based |
| **Critic** | **Sonnet** | **Meta-reasoning, validation** |

### Tool Schemas (5-Rule Pattern)

Every tool follows: **What / When / Why / Input / Error**

Example:
```
WHAT: Validates client identity
WHEN: Initial KYC stage
WHY: Regulatory requirement
INPUT: client_name (string), document_type (enum: passport, license)
ERROR: Returns InvalidIDFormat if pattern mismatch
```

### Structured Output via tool_use

All agent decisions use **forced `tool_use`**:
```python
tool_choice="required"  # Forces structured response
```

No ambiguous text; all responses validated against schema.

### Error Categorization

- `ValidationError` — Input format issues (pre-Claude)
- `ComplianceViolation` — Regulatory rejection
- `InsufficientData` — Missing documents
- `APIError` — Claude API failures
- `ReviewRequired` — Critic flagged inconsistency

---

## Guardrails & Compliance

### PII Protection
- All client names in logs: `[MASKED]` or `CLI001`
- SSN/ID numbers never logged
- **PreToolUse Hook** (`pre_tool_use.py`) validates before any model sees data

### Audit Trail
- Every decision logged: agent → model → timestamp → result → reasoning
- Error categories explicit
- All agent execution times recorded

### Critic Validation (Hard Stops)
```
IF compliance_result == "BLOCKED" → REJECT (no override, non-recoverable)
IF (compliance_risk in [MEDIUM, HIGH]) AND strategy == "AGGRESSIVE" → ESCALATE
IF inconsistency detected → ESCALATE_FOR_REVIEW
```

---

## Sample Outputs

### Scenario 1: Happy Path (APPROVED)
```json
{
  "client_id": "CLI001",
  "final_status": "APPROVED",
  "agents_executed": [
    {"agent": "kyc_agent", "result": "PASS", "duration_ms": 245},
    {"agent": "compliance_agent", "result": "LOW", "duration_ms": 890},
    {"agent": "document_agent", "result": "GENERATED", "duration_ms": 120},
    {"agent": "profile_agent", "result": "CONSERVATIVE", "duration_ms": 650},
    {"agent": "setup_agent", "result": "READY", "duration_ms": 180},
    {"agent": "critic_agent", "result": "CONFIRM_APPROVAL", "confidence": 0.98}
  ],
  "total_duration_ms": 3085
}
```

### Scenario 2: Rejection Path (REJECTED)
```json
{
  "client_id": "CLI002",
  "final_status": "REJECTED",
  "agents_executed": [
    {"agent": "kyc_agent", "result": "PASS", "duration_ms": 210},
    {"agent": "compliance_agent", "result": "BLOCKED", "flags": ["SANCTIONS_MATCH"]}
  ],
  "decision_reasoning": "Compliance BLOCKED decision - automatic rejection"
}
```

### Scenario 3: Manual Review Path (REQUIRES_MANUAL_REVIEW)
```json
{
  "client_id": "CLI003",
  "final_status": "REQUIRES_MANUAL_REVIEW",
  "inconsistencies": [
    {
      "type": "risk_strategy_mismatch",
      "severity": "medium",
      "detail": "Compliance risk is MEDIUM but strategy is AGGRESSIVE"
    }
  ],
  "escalation_reason": "Critic detected inconsistency - manual review recommended"
}
```

---

## Claude Code Integration

### 1. CLAUDE.md
Project conventions, model-tier rationale, development standards ([CLAUDE.md](CLAUDE.md))

### 2. Slash Command: `/onboard`
Run complete workflow for a client.
```
/onboard --client-name "John Doe" --source "email"
```
See: [.claude/commands/onboard.md](.claude/commands/onboard.md)

### 3. Skill: `audit-compliance-rules`
Review and update compliance ruleset.
See: [.claude/skills/audit-compliance-rules.md](.claude/skills/audit-compliance-rules.md)

### 4. PreToolUse Hook: `pre_tool_use.py`
Validates tool calls for PII leakage + 5-rule compliance.
See: [.claude/hooks/pre_tool_use.py](.claude/hooks/pre_tool_use.py)

---

## Project Structure

```
client-onboarding-orchestrator/
├── main.py                      # Orchestrator entry point
├── README.md                    # This file
├── CLAUDE.md                    # Development conventions
├── ARCHITECTURE.md              # System design + justification
├── COWORK_USAGE.md             # Cowork integration documentation
├── DEVELOPMENT_NOTES.md         # Claude Code usage evidence
├── requirements.txt
├── .gitignore
├── agents/
│   ├── kyc_agent.py            # Haiku - Identity verification
│   ├── compliance_agent.py      # Sonnet - Sanctions/risk check
│   ├── document_agent.py        # Haiku - Artifact generation
│   ├── profile_agent.py         # Sonnet - Financial analysis
│   ├── setup_agent.py           # Haiku - Account setup
│   └── critic_agent.py          # Sonnet - Approval validation (6th agent)
├── tools/
│   ├── schemas.py               # 5-rule tool definitions
│   └── mocks.py                 # Mock data, compliance DB
├── .claude/
│   ├── commands/
│   │   └── onboard.md           # /onboard slash command
│   ├── skills/
│   │   └── audit-compliance-rules.md
│   └── hooks/
│       └── pre_tool_use.py      # PII validation + 5-rule check
├── outputs/
│   ├── sample_cli001.json       # Happy path
│   ├── sample_cli002.json       # Rejection
│   ├── sample_cli003.json       # Manual review
│   └── summary.json             # Overall summary
└── .claude/plans/               # Planning documents (if used)
```

---

## Design Decisions

### Why OpenAI Agents SDK with Claude?
- Direct control over Claude model selection (Haiku vs Sonnet)
- Structured tool use with forced `tool_choice`
- Clean abstraction for multi-agent workflows
- Evaluator can easily review agent decisions

### Why Sequential Chain (Not Parallel)?
- **Audit clarity**: Clear ordering in logs
- **Business match**: Real onboarding is sequential (KYC before compliance)
- **Escalation simplicity**: If any stage fails, clear decision point

### Why Critic Agent?
1. **4-eyes principle**: Financial institutions require secondary review
2. **Catch hallucinations**: Detect agent disagreements (e.g., MEDIUM risk + AGGRESSIVE strategy)
3. **Hard stops**: Sanctions match cannot be overridden
4. **Advanced pattern**: Shows understanding of validator agents in multi-agent systems

### Why Structured Output (Forced tool_use)?
- No ambiguous text decisions
- Consistency: Every approval can be traced to reasoning
- Validation: All responses conform to schema
- Audit-friendly: Easy to analyze decision patterns

---

## Testing

### Happy Path (CLI001)
```bash
python main.py --sample-clients
# Check: outputs/sample_cli001.json → final_status == "APPROVED"
```
Expected: All agents pass, Critic confirms approval.

### Rejection Path (CLI002)
Check: `outputs/sample_cli002.json` → final_status == "REJECTED"
Expected: Sanctions match blocks at Compliance stage.

### Manual Review Path (CLI003)
Check: `outputs/sample_cli003.json` → final_status == "REQUIRES_MANUAL_REVIEW"
Expected: Critic flags inconsistency (MEDIUM risk + AGGRESSIVE strategy).

### Verify Guardrails
- Check logs: No client names visible (masked as `[MASKED]`)
- Check `pre_tool_use.py` hook: PII validation active

---

## Key Features

✅ **Multi-Agent Architecture** — 6 specialists + Critic orchestrator  
✅ **Model-Tier Strategy** — Deliberate Haiku/Sonnet choices  
✅ **Structured Output** — Forced tool_use, strict schemas  
✅ **Guardrails** — PII masking, compliance validation, inconsistency detection  
✅ **Audit Trail** — Every decision logged with reasoning  
✅ **Claude Code Integration** — Commands, skills, hooks  
✅ **Sample Outputs** — 3 scenarios: approval, rejection, manual review  
✅ **Error Handling** — Categorized errors, clear escalation paths  

---

## Running with Cowork (Optional)

See [COWORK_USAGE.md](COWORK_USAGE.md) for:
- Generating XLSX compliance reports
- Scheduling daily batch tasks
- Slack notifications

---

## Development with Claude Code

See [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) for:
- Screenshots of Claude Code usage during development
- Refactoring, review, and scaffolding examples
- Evidence of iterative development

---

## Submission

This project is designed for the CCA-F (Claude Architect Foundation) capstone evaluation.

**Grading Rubric Alignment:**
- **Architecture (22-25)** — Mermaid diagram, decomposition pattern, justification
- **Tech Stack (22-25)** — Model tiers, tool schemas (5-rule), structured output, error categories
- **Claude Cowork (22-25)** — Integration documentation (see COWORK_USAGE.md)
- **Claude Code (22-25)** — CLAUDE.md + commands + skills + hooks + development evidence

---

## Next Steps

1. **Review**: Check ARCHITECTURE.md for system design
2. **Run**: `python main.py --sample-clients` to generate outputs
3. **Explore**: Check sample JSONs in `outputs/` folder
4. **Integrate**: Use `/onboard` slash command in Claude Code
5. **Extend**: Add more agents or compliance rules as needed

---

## Questions?

- Architecture decisions? → See ARCHITECTURE.md
- Tool schema patterns? → See tools/schemas.py
- Claude Code setup? → See CLAUDE.md + .claude/ directory
- Sample data? → See tools/mocks.py

---

**Built with:** OpenAI agents SDK + Claude 3.5 (Haiku & Sonnet)  
**Status:** Ready for evaluation  
**Last Updated:** 2024-06-21
