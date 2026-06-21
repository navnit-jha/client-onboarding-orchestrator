# /onboard — Run Client Onboarding Workflow

## Syntax
```
/onboard --client-name "John Doe" --source "email"
/onboard --client-name "John Doe" --source "email" --override-risk "high"
```

## Description
Runs the complete 6-agent onboarding workflow for a new wealth management client.

**What it does:**
1. Validates client identity (KYC Agent - Haiku)
2. Screens compliance & sanctions (Compliance Agent - Sonnet)
3. Generates onboarding documents (Document Agent - Haiku)
4. Builds financial profile & strategy (Profile Agent - Sonnet)
5. Provisions account & schedules meetings (Setup Agent - Haiku)
6. Meta-validates entire chain with Critic (Critic Agent - Sonnet)

**Output:** JSON file in `outputs/` folder with full decision trace, agent execution times, and audit trail.

## Parameters

### --client-name (required)
Full name of the client. Example: "Jane Doe"

### --source (optional, default: "direct")
How client was sourced. Options: email, phone, referral, direct

### --override-risk (optional)
Override compliance risk for testing: low, medium, high

## Examples

### Happy path (standard approval):
```
/onboard --client-name "John Smith" --source "email"
```
Expected: APPROVED (all checks pass)

### High-risk path (manual review):
```
/onboard --client-name "High Net Worth Client" --override-risk "high"
```
Expected: REQUIRES_MANUAL_REVIEW (critic flags strategy mismatch)

### Rejection scenario (for testing):
```
/onboard --client-name "Jane Terrorist" --source "email"
```
Expected: REJECTED (sanctions match detected)

## Output
Creates JSON file: `outputs/sample_{client_id}_{timestamp}.json`

Contains:
- Final status (APPROVED / REJECTED / REQUIRES_MANUAL_REVIEW)
- Agent execution chain with timing for each
- All decisions and reasoning
- Flags and escalation reasons (if applicable)
- Generated documents and artifacts

## Implementation Notes
The command leverages the 6-agent orchestrator:
- Agents 1,3,5 use Claude 3.5 Haiku (fast validation, cost-optimized)
- Agents 2,4,6 use Claude 3.5 Sonnet (complex reasoning, accuracy-critical)
- Critic Agent (6th) validates entire chain and catches inconsistencies
- All decisions are structured, tagged with error categories, and audit-logged

## See Also
- ARCHITECTURE.md — Multi-agent system design
- COWORK_USAGE.md — Report generation and integrations
- agents/ directory — Individual agent implementations
