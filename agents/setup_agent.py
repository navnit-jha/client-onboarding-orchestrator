"""Account Setup Agent - Account provisioning and follow-ups.
Model: claude-3-5-haiku (rule-based configuration)
Purpose: Create account, schedule advisor meeting, send notifications.
"""

import json
import time
from typing import Dict, Any
from anthropic import Anthropic
from tools.mocks import create_mock_account, schedule_advisor_meeting
from tools.schemas import get_all_tools

client = Anthropic()

HAIKU_MODEL = "claude-3-5-haiku-20241022"

# Tools loaded dynamically in run_setup_agent

SETUP_SYSTEM_PROMPT = """You are an Account Setup Agent.
Your role: Provision accounts, create advisor relationships, schedule follow-ups.
Model: claude-3-5-haiku (configuration, rule-based)

Instructions:
1. Call create_account with client_id and account_type ("individual" for personal accounts)
2. Call schedule_advisor_meeting to set up initial consultation
3. Confirm account is ACTIVE and meeting is scheduled
4. Return account_id and meeting details
5. Prepare next steps (first deposit, welcome materials)

Be efficient and complete.
"""

def run_setup_agent(client_data: Dict[str, Any], prior_results: Dict[str, Any]) -> Dict[str, Any]:
    """Setup account for a client."""
    start_time = time.time()

    # Check prior stages
    for stage in ["kyc_agent", "compliance_agent", "document_agent", "profile_agent"]:
        stage_result = prior_results.get(stage, {})
        if stage_result.get("decision") in ["FAIL", "BLOCKED", "SKIPPED", "REJECTED"]:
            return {
                "agent": "setup_agent",
                "decision": "SKIPPED",
                "reasoning": f"Prior stage ({stage}) did not complete - account not setup",
                "duration_ms": 0
            }

    user_message = f"""
Setup account for this client:
- Name: {client_data['name']}
- Client ID: {client_data['client_id']}
- Risk Strategy: {prior_results.get('profile_agent', {}).get('decision', 'MODERATE')}

Tasks:
1. Call create_account with account_type="individual"
2. Call schedule_advisor_meeting for initial consultation
3. Return account_id (format: ACC-XXXXXX)
4. Confirm meeting is scheduled
5. List next steps: Upload ID, Set up direct deposit, Review materials
"""

    try:
        # Get setup tools
        all_tools = get_all_tools()
        setup_tools = [t for t in all_tools if t['function']['name'] in ['create_account', 'schedule_advisor_meeting']]

        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=1200,
            tools=setup_tools,
            system=SETUP_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Process response
        account_id = None
        meeting_id = None
        reasoning = None

        for block in response.content:
            if block.type == "text":
                reasoning = block.text

            elif block.type == "tool_use":
                tool_name = block.name

                if tool_name == "create_account":
                    account_data = create_mock_account(client_data)
                    account_id = account_data["account_id"]

                elif tool_name == "schedule_advisor_meeting":
                    meeting_data = schedule_advisor_meeting(client_data)
                    meeting_id = meeting_data["meeting_id"]

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "agent": "setup_agent",
            "model": HAIKU_MODEL,
            "decision": "READY",
            "account_id": account_id,
            "meeting_id": meeting_id,
            "meeting_date": "2024-07-05",
            "next_steps": [
                "Upload government ID",
                "Set up direct deposit",
                "Review investment materials",
                "Attend advisor meeting"
            ],
            "reasoning": reasoning or "Account setup complete, ready for onboarding",
            "duration_ms": duration_ms,
            "client_id": client_data.get("client_id")
        }

        return result

    except Exception as e:
        return {
            "agent": "setup_agent",
            "error": str(e),
            "error_category": "APIError",
            "decision": "ERROR"
        }


if __name__ == "__main__":
    from agents.kyc_agent import run_kyc_agent
    from agents.compliance_agent import run_compliance_agent
    from agents.document_agent import run_document_agent
    from agents.profile_agent import run_profile_agent
    from tools.mocks import SAMPLE_CLIENTS

    test_client = SAMPLE_CLIENTS[0]
    print("Testing Setup Agent...")

    results = {}
    results["kyc_agent"] = run_kyc_agent(test_client)
    results["compliance_agent"] = run_compliance_agent(test_client, results["kyc_agent"])
    results["document_agent"] = run_document_agent(test_client, results["compliance_agent"])
    results["profile_agent"] = run_profile_agent(test_client, results)
    setup_result = run_setup_agent(test_client, results)

    print("Setup Result:")
    print(json.dumps(setup_result, indent=2))
