# Claude Cowork Integration Guide

## Overview
This document describes how Claude Cowork is (or could be) used to enhance the Client Onboarding Orchestrator capstone project.

## Rationale for Cowork Usage

Claude Cowork excels at:
1. **File Output Generation** — Creating XLSX/DOCX reports
2. **Scheduled Tasks** — Running batch jobs on intervals
3. **Connectors** — Integrating with external systems (Slack, Gmail, Drive)

Our capstone benefits from Cowork in these specific areas:

---

## 1. XLSX Report Generation (`/xlsx` Skill)

### Use Case
Generate daily onboarding summary reports for compliance review.

### What Gets Generated
```
Daily_Onboarding_Report_2024-06-21.xlsx
├── Sheet: Summary
│   ├── Clients Processed: 47
│   ├── Approved: 43
│   ├── Rejected: 2
│   ├── Requires Review: 2
│   ├── Avg Processing Time: 3,150ms
│   └── Success Rate: 91.5%
├── Sheet: Approvals (43 clients)
│   ├── Client ID | Name | Risk Level | Account ID | Strategy
├── Sheet: Rejections (2 clients)
│   ├── Client ID | Reason | Compliance Flag
├── Sheet: Manual Review (2 clients)
│   ├── Client ID | Inconsistency | Recommended Action
└── Sheet: Risk Distribution
    ├── LOW: 15 clients
    ├── MEDIUM: 25 clients
    ├── HIGH: 7 clients
```

### How to Invoke (Cowork Manual Setup)
1. Open Claude Cowork desktop app
2. Connect to capstone project folder
3. Invoke `/xlsx` skill with request:
   ```
   Generate daily onboarding summary for 2024-06-21
   Include: approval rate, risk distribution, agent timing stats
   Source: outputs/summary.json
   ```
4. Cowork generates `Daily_Onboarding_Report_2024-06-21.xlsx`

### Why Cowork?
- ✅ Excel generation cleaner than manual JSON → XLSX conversion
- ✅ Non-technical compliance team can read reports
- ✅ Templated format ensures consistency
- ✅ One command vs 50 lines of Python code

---

## 2. Scheduled Daily Batch Task

### Use Case
Run overnight compliance re-check on existing clients.

### What the Task Does
```
Every night at 11:00 PM:
1. Load all existing client records from database
2. Re-run Compliance Agent on each
3. Flag any risk-level changes
4. Generate report of changes
5. Send Slack alert if HIGH_RISK or newly BLOCKED clients found
```

### How to Set Up (Cowork Manual Setup)
1. Open Cowork → Settings → Scheduled Tasks
2. Create new task:
   ```
   Name: overnight-compliance-recheck
   Schedule: 0 23 * * * (11 PM daily)
   Trigger Command: python agents/compliance_agent.py --batch-mode
   ```
3. Cowork handles scheduling, logging, error handling, retries

### Why Cowork?
- ✅ Cowork handles cron scheduling — we don't need to manage cron
- ✅ Handles retries, logging, notifications automatically
- ✅ Can integrate with other Cowork skills (Slack notifications)
- ✅ Shows auditor that compliance checks are automated, not manual

---

## 3. Slack Connector Integration

### Use Case
Alert compliance team when high-risk clients are flagged for review.

### What Gets Sent
```
Slack Message to #compliance-alerts:

🔔 Manual Review Required — 1 client needs review

Client: CLI003
Risk Level: MEDIUM
Issue: Strategy mismatch (AGGRESSIVE recommended for conservative profile)
Recommended Action: Review with senior advisor before approval

Link: http://localhost:8000/clients/cli003/review
```

### How to Set Up (Cowork Manual Setup)
1. Open Cowork → Connectors → authorize Slack
2. Choose channel: `#compliance-alerts`
3. In agent code, call:
   ```python
   cowork.slack.send_message(
       channel="#compliance-alerts",
       text=f"Manual Review Required: {client_name}"
   )
   ```
4. On agent escalation, Slack is notified

### Why Cowork?
- ✅ Asynchronous notifications — humans see alerts immediately
- ✅ Cowork handles Slack auth + retries
- ✅ Team doesn't need to check system — alerts come to them
- ✅ Audit trail: Slack message history is timestamped

---

## 4. Google Drive Integration (Optional)

### Use Case
Save generated reports and audit logs to Drive for document control.

### How to Set Up
1. Cowork → Connectors → authorize Google Drive
2. Create folder: `Capstone_Onboarding_Reports`
3. On report generation:
   ```python
   cowork.drive.upload(
       file="outputs/summary.json",
       folder="Capstone_Onboarding_Reports",
       name=f"report_{date}.json"
   )
   ```

---

## 5. Email Integration (Optional)

### Use Case
Send daily summary to compliance manager's inbox.

### How to Set Up
1. Cowork → Connectors → authorize Gmail
2. On scheduled task completion:
   ```python
   cowork.gmail.send(
       to="compliance.manager@example.com",
       subject=f"Onboarding Report — {date}",
       body=f"See attached: {report_file}",
       attachment="Daily_Onboarding_Report_2024-06-21.xlsx"
   )
   ```

---

## Implementation Evidence

### Rationale for NOT Using Cowork in This Capstone
**Important**: If you choose NOT to use Cowork for this capstone, here's why that's valid:

> "Client onboarding is fully automated by the multi-agent system. Cowork would be valuable for external integrations (Slack alerts, Excel reporting), but:
> 1. Project scope is agent orchestration, not reporting pipelines
> 2. Capstone runs locally with mocked data (no real Slack/Drive needed)
> 3. Evaluation is on agent design + Claude Code usage, not infrastructure
> 4. Time better spent perfecting agent logic than setting up connectors"

This is a valid choice for a project focused on multi-agent orchestration.

---

## Optional: Implementing Cowork Integration

If you choose to integrate Cowork features:

### XLSX Report Generation:
1. **Create Excel report** showing onboarding summary
   - Clients processed, approval rates, risk distribution
   - Save to: `outputs/cowork_report.xlsx`

### Scheduled Tasks:
1. **Set up overnight compliance recheck** task
   - Schedule: Daily at 11 PM
   - Action: Re-verify all existing clients

### Slack Notifications:
1. **Configure Slack alerts** for manual review cases
   - Channel: `#compliance-alerts`
   - Trigger: When Critic escalates inconsistency

---

## How to Screenshot/Document Cowork Usage

### Option 1: Screenshot Flow
1. Open Cowork
2. Open capstone folder
3. Invoke `/xlsx` skill → shows skill in action
4. Save screenshot: `screenshots/cowork_skill_xlsx.png`
5. Repeat for other skills

### Option 2: Transcript
1. Run skill in Cowork
2. Copy transcript (Cowork → Show Transcript)
3. Save to: `transcripts/cowork_usage_2024-06-21.md`

### Option 3: Inline in README
Document in this file with inline examples and expected outputs.

---

## File References

- Main output: `outputs/summary.json`
- Report template: See section 1 above
- Slack message template: See section 3 above
- Expected files: `screenshots/`, `transcripts/`

---

## Decision Framework

### Use Cowork for:
✅ Report generation (XLSX, DOCX)  
✅ External notifications (Slack, Email)  
✅ Scheduled/recurring tasks  
✅ File management (Drive, OneDrive)  

### Don't use Cowork for:
❌ Core agent logic (implement in Python)  
❌ Tool definitions (define in tools/schemas.py)  
❌ Data mocking (use tools/mocks.py)  

---

## Next Steps

1. **Decide** whether to implement Cowork integrations
2. **If implementing**: Set up XLSX reports, scheduled tasks, or Slack notifications
3. **If not implementing**: Current setup is focused on core multi-agent functionality
4. **Document**: Any implementation details in this file

---

## See Also
- ARCHITECTURE.md — Core agent design
- README.md — Main project documentation
- CLAUDE.md — Development conventions
