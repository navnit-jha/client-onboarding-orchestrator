"""Compliance Check Agent - Sanctions screening and risk assessment.
Model: claude-3-5-sonnet (nuanced reasoning required)
Purpose: Assess regulatory compliance risk, check sanctions lists, assign risk category.
"""

import json
import time
from typing import Dict, Any
from openai import OpenAI
from tools.mocks import check_sanctions, assess_risk_score, mask_pii
from tools.schemas import TOOL_SCHEMAS

client = OpenAI()

SONNET_MODEL = "claude-3-5-sonnet-20241022"

COMPLIANCE_TOOLS = [
    TOOL_SCHEMAS["sanctions_check"],
    TOOL_SCHEMAS["assess_compliance_risk"],
]

COMPLIANCE_SYSTEM_PROMPT = """You are a Compliance Risk Assessment Agent.
Your role: Screen clients against sanctions lists and assign compliance risk category.
Model: claude-3-5-sonnet (nuanced reasoning, accuracy-critical)

Instructions:
1. Check sanctions lists - if match found, immediately return BLOCKED (non-recoverable)
2. Assess risk factors: income level, prior flags, documentation completeness
3. Assign risk category: LOW, MEDIUM, HIGH, or BLOCKED
4. Provide detailed reasoning for the risk assessment
5. Flag any concerning patterns

This is a regulatory function. Be thorough and conservative.
"""

def run_compliance_agent(client_data: Dict[str, Any], kyc_result: Dict[str, Any]) -> Dict[str, Any]:
    """Run compliance check for a client."""
    start_time = time.time()

    # Only proceed if KYC passed
    if kyc_result.get("decision") != "PASS":
        return {
            "agent": "compliance_agent",
            "decision": "SKIPPED",
            "reasoning": "KYC failed - compliance check not performed",
            "duration_ms": 0
        }

    masked_email = mask_pii(client_data.get("email", ""), "email")

    user_message = f"""
Perform compliance assessment for this client:
- Name: {client_data['name']}
- Email: {masked_email}
- Income: ${client_data['income']:,}
- Net Worth: ${client_data['net_worth']:,}
- Investment Experience: {client_data['investment_experience']}

Tasks:
1. Call sanctions_check to screen against OFAC/UN/EU lists
2. If sanctions match found → return BLOCKED (non-recoverable)
3. If no match, call assess_compliance_risk with income/networth/experience
4. Return risk category (LOW/MEDIUM/HIGH/BLOCKED) with reasoning
5. Include any compliance flags or concerns
"""

    try:
        response = client.beta.messages.create(
            model=SONNET_MODEL,
            max_tokens=1500,
            tools=COMPLIANCE_TOOLS,
            system=COMPLIANCE_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Process response
        decision = "LOW"  # Default
        reasoning = None
        risk_score = 0
        flags = []

        for content_block in response.content:
            if hasattr(content_block, 'text'):
                reasoning = content_block.text

            elif content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input

                if tool_name == "sanctions_check":
                    sanctions_result = check_sanctions(
                        client_data.get("email", ""),
                        client_data.get("name", "")
                    )
                    if sanctions_result["is_sanctioned"]:
                        decision = "BLOCKED"
                        reasoning = "Sanctions list match - automatic rejection"
                        flags = ["SANCTIONS_MATCH"]

                elif tool_name == "assess_compliance_risk" and decision != "BLOCKED":
                    risk_result = assess_risk_score(client_data)
                    decision = risk_result["risk_level"]
                    reasoning = risk_result["reasoning"]
                    risk_score = risk_result["score"]
                    flags = risk_result["flags"]

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "agent": "compliance_agent",
            "model": SONNET_MODEL,
            "decision": decision,
            "risk_score": risk_score,
            "flags": flags,
            "reasoning": reasoning or "Compliance assessment complete",
            "duration_ms": duration_ms,
            "client_id": client_data.get("client_id")
        }

        return result

    except Exception as e:
        return {
            "agent": "compliance_agent",
            "error": str(e),
            "error_category": "APIError",
            "decision": "HIGH"
        }


if __name__ == "__main__":
    from agents.kyc_agent import run_kyc_agent
    from tools.mocks import SAMPLE_CLIENTS

    test_client = SAMPLE_CLIENTS[0]
    print("Testing Compliance Agent...")
    kyc_result = run_kyc_agent(test_client)
    compliance_result = run_compliance_agent(test_client, kyc_result)
    print("Compliance Result:")
    print(json.dumps(compliance_result, indent=2))
