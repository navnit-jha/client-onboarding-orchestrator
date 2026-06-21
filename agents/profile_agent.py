"""Financial Profile Agent - Investment strategy and risk assessment.
Model: claude-3-5-sonnet (complex reasoning required)
Purpose: Build client investment profile, assess risk tolerance, recommend strategy.
"""

import json
import time
from typing import Dict, Any
from anthropic import Anthropic
from tools.schemas import get_all_tools

client = Anthropic()

SONNET_MODEL = "claude-3-5-sonnet-20241022"

# Tools loaded dynamically in run_profile_agent

PROFILE_SYSTEM_PROMPT = """You are a Financial Profile Agent.
Your role: Analyze client profile, assess risk tolerance, recommend investment strategy.
Model: claude-3-5-sonnet (nuanced financial analysis)

Instructions:
1. Call assess_risk_tolerance with client income, experience, time_horizon, risk score
2. Based on risk tolerance, call recommend_investment_strategy
3. Strategies: CONSERVATIVE (40/60 stocks/bonds), MODERATE (60/40), AGGRESSIVE (80/20)
4. Provide rationale for the strategy recommendation
5. Note any concerns or special circumstances

Be thorough in reasoning. Consider life stage, income stability, experience level.
"""

def run_profile_agent(client_data: Dict[str, Any], prior_results: Dict[str, Any]) -> Dict[str, Any]:
    """Build financial profile for a client."""
    start_time = time.time()

    # Check prior stages
    for stage in ["kyc_agent", "compliance_agent", "document_agent"]:
        if prior_results.get(stage, {}).get("decision") in ["FAIL", "BLOCKED", "SKIPPED"]:
            return {
                "agent": "profile_agent",
                "decision": "SKIPPED",
                "reasoning": f"Prior stage ({stage}) did not complete - profile not assessed",
                "duration_ms": 0
            }

    # Calculate risk score from investment experience
    experience_scores = {
        "none": 20,
        "1-3 years": 40,
        "3-5 years": 60,
        "5+ years": 80
    }
    risk_score = experience_scores.get(client_data.get("investment_experience", "none"), 40)

    user_message = f"""
Build financial profile for this client:
- Name: {client_data['name']}
- Income: ${client_data['income']:,}
- Net Worth: ${client_data['net_worth']:,}
- Investment Experience: {client_data['investment_experience']}
- Stated Risk Tolerance: {client_data['risk_tolerance']}
- Time Horizon: Long-term (retirement planning)

Tasks:
1. Call assess_risk_tolerance with provided data
2. Call recommend_investment_strategy based on tolerance
3. Return strategy (CONSERVATIVE/MODERATE/AGGRESSIVE) with reasoning
4. Include asset allocation suggestion (stocks/bonds/alternatives)
5. Note any concerns about experience vs risk profile
"""

    try:
        # Get profile tools
        all_tools = get_all_tools()
        profile_tools = [t for t in all_tools if t['function']['name'] in ['assess_risk_tolerance', 'recommend_investment_strategy']]

        response = client.messages.create(
            model=SONNET_MODEL,
            max_tokens=1500,
            tools=profile_tools,
            system=PROFILE_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Process response
        strategy = "MODERATE"  # Default
        reasoning = None
        allocation = {}

        for block in response.content:
            if block.type == "text":
                reasoning = block.text

            elif block.type == "tool_use":
                tool_name = block.name

                if tool_name == "recommend_investment_strategy":
                    # Determine strategy based on stated risk tolerance
                    stated_risk = client_data.get("risk_tolerance", "moderate").lower()
                    if stated_risk == "conservative":
                        strategy = "CONSERVATIVE"
                        allocation = {"stocks": 40, "bonds": 60, "alternatives": 0}
                    elif stated_risk == "aggressive":
                        strategy = "AGGRESSIVE"
                        allocation = {"stocks": 80, "bonds": 15, "alternatives": 5}
                    else:
                        strategy = "MODERATE"
                        allocation = {"stocks": 60, "bonds": 35, "alternatives": 5}

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "agent": "profile_agent",
            "model": SONNET_MODEL,
            "decision": strategy,
            "asset_allocation": allocation,
            "reasoning": reasoning or f"Strategy: {strategy} aligned with client profile",
            "duration_ms": duration_ms,
            "client_id": client_data.get("client_id")
        }

        return result

    except Exception as e:
        return {
            "agent": "profile_agent",
            "error": str(e),
            "error_category": "APIError",
            "decision": "MODERATE"
        }


if __name__ == "__main__":
    from agents.kyc_agent import run_kyc_agent
    from agents.compliance_agent import run_compliance_agent
    from agents.document_agent import run_document_agent
    from tools.mocks import SAMPLE_CLIENTS

    test_client = SAMPLE_CLIENTS[0]
    print("Testing Profile Agent...")

    results = {}
    results["kyc_agent"] = run_kyc_agent(test_client)
    results["compliance_agent"] = run_compliance_agent(test_client, results["kyc_agent"])
    results["document_agent"] = run_document_agent(test_client, results["compliance_agent"])
    profile_result = run_profile_agent(test_client, results)

    print("Profile Result:")
    print(json.dumps(profile_result, indent=2))
