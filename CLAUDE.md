# Client Onboarding Orchestrator — Development Conventions

## Project Overview
A wealth management client onboarding multi-agent system using OpenAI agents SDK with Claude models. Demonstrates agentic AI best practices with structured decision-making, guardrails, and audit trails.

## Development Conventions

### Model Tier Selection
- **Claude 3.5 Haiku**: Document validation, routing decisions, account setup (< 100ms operations, cost-optimized)
  - Agents: KYC, Document Generation, Account Setup
  - When: Rule-based checks, data extraction, straightforward logic
  
- **Claude 3.5 Sonnet**: Complex analysis, compliance decisions, meta-reasoning (300-800ms, accuracy-optimized)
  - Agents: Compliance Check, Financial Profile, Critic Review
  - When: Nuanced reasoning, multi-factor assessment, approval authority

### Tool Schema Pattern (5-Rule)
All tools follow this structure:
1. **What**: Clear name describing the action
2. **When**: Condition or context for invocation
3. **Why**: Business rationale
4. **Input**: Complete JSON schema with validation rules
5. **Error**: Explicit error cases and handling

Example:
```json
{
  "name": "verify_identity",
  "description": "What: Validates client identity. When: Initial KYC stage. Why: Regulatory requirement. Input: client_name (string), document_type (enum), id_number (string). Error: InvalidIDFormat if pattern mismatch.",
  "input_schema": {...}
}
```

### Structured Output & tool_use
- All agent decisions returned via **forced tool_use** (not raw text)
- `tool_choice="required"` enforces structured responses
- Response schema validates decision + reasoning + confidence score
- No ambiguous "yes/no" strings — always structured JSON

### Error Handling & Categorization
- `ValidationError`: Input format issues (pre-Claude validation)
- `ComplianceViolation`: Regulatory rejection (explicit category in output)
- `InsufficientData`: Missing required documents (escalation flag)
- `APIError`: Claude API failures (retry with exponential backoff)
- `ReviewRequired`: Critic flagged inconsistency (manual intervention)

### PII Protection & Audit Trail
- All client identifiers masked: `[MASKED]` or `CLI001` format in logs
- SSN/ID numbers never in logs or AI model inputs
- PreToolUse hook validates all tool parameters before execution
- Every decision logged: agent → model → timestamp → result → reasoning

### Code Organization
```
agents/        → Individual agent implementations
tools/         → Shared schemas and mocks
.claude/       → Claude Code configuration (commands, skills, hooks)
outputs/       → Sample execution results (JSON)
```

## Running the Capstone

### Install dependencies
```bash
pip install -r requirements.txt
```

### Set API key
```bash
export OPENAI_API_KEY="sk-..."
```

### Run full onboarding workflow (3 sample clients)
```bash
python main.py --sample-clients
```
Outputs 3 JSON files to `outputs/` folder: approval, rejection, manual review scenarios.

### Test individual agent
```bash
python agents/kyc_agent.py --test-client "John Doe"
```

### Use slash command (in Claude Code)
```
/onboard --client-name "John Doe" --source "email"
```

## Key Design Decisions

### Why 6 Agents (Including Critic)?
- **5 Specialists** (KYC, Compliance, Documents, Profile, Setup): Each owns a domain
- **1 Critic**: Validates the entire chain, detects hallucinations, implements "4-eyes principle"
- **Alternative rejected**: Single agent would sacrifice specialization; chatbot lacks audit trail; workflow engine can't handle exceptions

### Why Sequential with Critic?
- **Sequential agents 1-5**: Deterministic ordering (each input depends on prior output), matches real onboarding workflow
- **Critic as final gate**: Reviews all decisions, catches inconsistencies, implements compliance "check & verify" practice
- **Escalation path**: Critic can override approval if risk threshold crossed

### Why Haiku vs Sonnet?
- **Haiku for validation** (KYC docs exist? Account fields populated?): Fast, cost-effective, sufficient accuracy
- **Sonnet for judgment** (Is this a compliance risk? What's optimal strategy?): Nuanced reasoning, handles edge cases, lower error rate
- **Better than all-Sonnet**: Saves cost while maintaining quality where it matters; demonstrates deliberate model-tier choices

## Files You'll Work With

| File | Purpose |
|------|---------|
| `main.py` | Entry point, orchestrates agents |
| `agents/kyc_agent.py` | Identity verification (Haiku) |
| `agents/compliance_agent.py` | Sanctions/risk check (Sonnet) |
| `agents/document_agent.py` | Artifact generation (Haiku) |
| `agents/profile_agent.py` | Financial analysis (Sonnet) |
| `agents/setup_agent.py` | Account setup (Haiku) |
| `agents/critic_agent.py` | Approval validation (Sonnet) |
| `tools/schemas.py` | Tool definitions |
| `tools/mocks.py` | Mock data and databases |
| `.claude/commands/onboard.md` | `/onboard` slash command |
| `.claude/skills/audit-compliance-rules.md` | Audit skill |
| `.claude/hooks/pre_tool_use.py` | PII validation hook |

## Testing & Verification

- **Happy path**: Client passes all checks → APPROVED (see `outputs/sample_approval.json`)
- **Rejection path**: Client fails compliance → REJECTED (see `outputs/sample_rejection.json`)
- **Escalation path**: Critic detects inconsistency → MANUAL_REVIEW (see `outputs/sample_manual_review.json`)
- **Guardrails**: PII always masked, all errors categorized, audit trail complete

## Next Steps

1. Review architecture diagram in ARCHITECTURE.md
2. Run `python main.py --sample-clients` to generate outputs
3. Check COWORK_USAGE.md for Claude Cowork integration
4. See DEVELOPMENT_NOTES.md for Claude Code usage evidence
