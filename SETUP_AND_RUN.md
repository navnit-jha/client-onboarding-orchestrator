# Client Onboarding Orchestrator - Setup & Run Guide

## Prerequisites

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **Anthropic API Key** (free tier available)
   - Get from: https://console.anthropic.com/
   - Create account → API keys → Create new key

3. **Git** (optional, for cloning from GitHub)

---

## Installation Steps

### Step 1: Navigate to Project
```bash
cd /c/Users/vmuser/Documents/capstone
```

### Step 2: Create Virtual Environment (Recommended)

**Windows PowerShell:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `anthropic==0.28.0` - Anthropic SDK for Claude models
- `python-dotenv==1.0.0` - Environment variable management

### Step 4: Set Anthropic API Key

**Option A: Environment Variable (Recommended)**

Windows PowerShell:
```bash
$env:ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"
```

Windows Command Prompt:
```bash
set ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

Mac/Linux:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

**Option B: Create .env File**

Create `/c/Users/vmuser/Documents/capstone/.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

---

## Running the Project

### Main Command: Run with 3 Sample Clients

```bash
python main.py --sample-clients
```

This will:
- ✅ Process 3 sample client scenarios (happy path, rejection, manual review)
- ✅ Run all 6 agents for each client
- ✅ Generate JSON output files
- ✅ Display progress in console
- ✅ Save outputs to `outputs/` folder

### Expected Console Output

```
======================================================================
CLIENT ONBOARDING ORCHESTRATOR - CAPSTONE PROJECT
Multi-Agent Workflow with 6-Agent Chain + Critic Validation
======================================================================

======================================================================
ONBOARDING WORKFLOW: CLI001 - John Smith
======================================================================

[1/6] KYC Verification Agent (Haiku)...
      Result: PASS (245ms)
[2/6] Compliance Check Agent (Sonnet)...
      Result: LOW (890ms)
[3/6] Document Generation Agent (Haiku)...
      Result: GENERATED (120ms)
[4/6] Financial Profile Agent (Sonnet)...
      Result: CONSERVATIVE (650ms)
[5/6] Account Setup Agent (Haiku)...
      Result: READY (180ms)
[6/6] CRITIC Agent (Sonnet) - Final Validation...
      Result: CONFIRM_APPROVAL (320ms)

      ==================================================================
      FINAL DECISION: APPROVED
      Total Duration: 3085ms
      Critic Confidence: 98%
      ==================================================================

[OK] Saved: outputs/sample_cli001.json
```

---

## Output Files

After running, check these files:

```
outputs/
├── sample_cli001.json      # Happy path (APPROVED)
├── sample_cli002.json      # Rejection (BLOCKED)
├── sample_cli003.json      # Manual review (ESCALATED)
└── summary.json            # Summary statistics
```

### View JSON Output

**Windows PowerShell:**
```bash
Get-Content outputs/sample_cli001.json
```

**Mac/Linux or any OS with Python:**
```bash
python -m json.tool outputs/sample_cli001.json
```

**Or open with text editor:**
```bash
notepad outputs/sample_cli001.json  # Windows
cat outputs/sample_cli001.json      # Mac/Linux
```

---

## What Each Output Contains

### sample_cli001.json (APPROVED)
- Client passes all 6 agents
- Critic confirms approval
- Account created
- Timing for each agent

### sample_cli002.json (REJECTED)
- Client matches sanctions list
- Blocked at Compliance stage
- No further agents run
- Hard stop decision

### sample_cli003.json (REQUIRES_MANUAL_REVIEW)
- Client passes initial checks
- Critic detects inconsistency (risk/strategy mismatch)
- Escalated for manual review
- Issue details provided

---

## Quick Reference - What You Need

| Item | Status | Details |
|---|---|---|
| Python 3.8+ | ✅ Required | Check: `python --version` |
| Anthropic API Key | ✅ Required | Get from: console.anthropic.com |
| Project Files | ✅ Required | main.py, agents/*.py, tools/*.py |
| requirements.txt | ✅ Required | Run: `pip install -r requirements.txt` |
| .env or env var | ✅ Required | Set ANTHROPIC_API_KEY |
| Virtual Env | ⚠️ Recommended | Optional but best practice |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### "APIError: Unauthorized - invalid API key"
1. Generate new API key: https://console.anthropic.com/
2. Set it again: `$env:ANTHROPIC_API_KEY = "sk-ant-..."`
3. Or add to .env file

### "ModuleNotFoundError: No module named 'agents' or 'tools'"
Make sure you're in the project root:
```bash
cd /c/Users/vmuser/Documents/capstone
ls -la  # Should see main.py, agents/, tools/
```

### Script doesn't run
- Verify Python is in PATH: `python --version`
- Activate virtual environment first
- Check API key is set: `echo $env:ANTHROPIC_API_KEY` (PowerShell)

---

## Project Structure

```
capstone/
├── main.py                      ← RUN THIS
├── requirements.txt             ← pip install
├── README.md                    ← Documentation
├── SETUP_AND_RUN.md            ← This file
│
├── agents/                      ← 6 Agent impls
│   ├── kyc_agent.py
│   ├── compliance_agent.py
│   ├── document_agent.py
│   ├── profile_agent.py
│   ├── setup_agent.py
│   └── critic_agent.py
│
├── tools/                       ← Tool definitions
│   ├── schemas.py               ← 10 tool definitions
│   └── mocks.py                 ← Mock data + compliance DB
│
└── outputs/                     ← Generated outputs
    ├── sample_cli001.json
    ├── sample_cli002.json
    ├── sample_cli003.json
    └── summary.json
```

---

## Quick Start (TL;DR)

```bash
# 1. Navigate to project
cd /c/Users/vmuser/Documents/capstone

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key (Windows PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-your-key"

# 4. Run
python main.py --sample-clients

# 5. Check outputs
Get-Content outputs/sample_cli001.json
```

---

## Next Steps

1. ✅ Run `python main.py --sample-clients`
2. ✅ Check `outputs/` folder for JSON files
3. ✅ Review the architecture in `ARCHITECTURE.md`
4. ✅ Explore agent implementations in `agents/` folder
5. ✅ Customize clients in `tools/mocks.py` to test different scenarios

---

**Questions?**
- See README.md for architecture overview
- See ARCHITECTURE.md for system design
- See CLAUDE.md for development conventions
