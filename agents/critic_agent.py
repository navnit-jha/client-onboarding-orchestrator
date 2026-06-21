"""CRITIC Agent - Meta-validation and approval review (6th Agent).
Model: claude-3-5-sonnet (meta-reasoning, validation)
Purpose: Validate entire approval chain, catch inconsistencies, implement 4-eyes principle.

Why Critic Agent?
1. Catches hallucinations: Detects agent disagreements (e.g., Compliance says MEDIUM but Profile recommends AGGRESSIVE)
2. Implements 4-eyes principle: Financial industry requires secondary review for approvals
3. Hard stops: If Compliance returns BLOCKED (sanctions), Critic automatically rejects
4. Audit trail: Final approval signed by Critic agent + timestamp
"""

import json
import time
from typing import Dict, Any
from openai import OpenAI
from tools.schemas import TOOL_SCHEMAS

client = OpenAI()

SONNET_MODEL = "claude-3-5-sonnet-20241022"

CRITIC_TOOLS = [
    TOOL_SCHEMAS["validate_approval_chain"],
    TOOL_SCHEMAS["detect_inconsistencies"],
]

CRITIC_SYSTEM_PROMPT = """You are a CRITIC AGENT - Final approval validator for wealth management onboarding.
Your role: Meta-validate entire approval chain, catch hallucinations, implement 4-eyes principle.
Model: claude-3-5-sonnet (meta-reasoning, validation expertise)

Critical Rules (NON-NEGOTIABLE):
1. If compliance_result == "BLOCKED" → REJECT (no override, non-recoverable)
2. If compliance_risk in [MEDIUM, HIGH] AND strategy == AGGRESSIVE → ESCALATE (potential mismatch)
3. If INCONSISTENCY detected → ESCALATE (human review required)
4. If all stages PASS and risk acceptable → CONFIRM_APPROVAL

Tasks:
1. Validate entire chain: KYC → Compliance → Documents → Profile → Setup
2. Check for contradictions (e.g., high compliance risk + aggressive strategy)
3. Apply hard stops: BLOCKED cannot be overridden
4. Make final decision: CONFIRM_APPROVAL, ESCALATE_FOR_REVIEW, or REJECT

You are the final checkpoint. Be analytical but empowering. Default to approval if no red flags.
"""

def run_critic_agent(client_data: Dict[str, Any], all_results: Dict[str, Any]) -> Dict[str, Any]:
    """Run meta-validation of entire approval chain (6th agent - Critic)."""
    start_time = time.time()

    # Extract results from prior agents
    kyc_result = all_results.get("kyc_agent", {})
    compliance_result = all_results.get("compliance_agent", {})
    document_result = all_results.get("document_agent", {})
    profile_result = all_results.get("profile_agent", {})
    setup_result = all_results.get("setup_agent", {})

    kyc_decision = kyc_result.get("decision", "UNKNOWN")
    compliance_risk = compliance_result.get("decision", "UNKNOWN")
    compliance_flags = compliance_result.get("flags", [])
    profile_strategy = profile_result.get("decision", "MODERATE")
    docs_generated = document_result.get("documents_count", 0) > 0
    setup_status = setup_result.get("decision", "UNKNOWN")

    user_message = f"""
CRITIC AGENT: Final approval validation for client {client_data['client_id']}

APPROVAL CHAIN RESULTS:
1. KYC: {kyc_decision}
2. Compliance: {compliance_risk} (flags: {compliance_flags})
3. Documents: {docs_generated} (generated)
4. Profile: {profile_strategy}
5. Setup: {setup_status}

ANALYSIS REQUIRED:
1. Call validate_approval_chain with all results
2. Check for contradictions:
   - Is {compliance_risk} risk compatible with {profile_strategy} strategy?
   - Are there any BLOCKED flags that override everything?
3. Call detect_inconsistencies if needed
4. Make FINAL decision: CONFIRM_APPROVAL / ESCALATE_FOR_REVIEW / REJECT

Strict rule: If compliance_risk == "BLOCKED", reject immediately (non-recoverable).
"""

    try:
        response = client.beta.messages.create(
            model=SONNET_MODEL,
            max_tokens=1500,
            tools=CRITIC_TOOLS,
            system=CRITIC_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Process response
        critic_decision = "UNKNOWN"
        reasoning = None
        flags = []
        inconsistencies = []

        # Apply hard stop: BLOCKED cannot be overridden
        if compliance_risk == "BLOCKED":
            critic_decision = "REJECT"
            reasoning = "Compliance BLOCKED decision - automatic rejection (hard stop)"
            flags = ["HARD_STOP_BLOCKED"]
        else:
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    reasoning = content_block.text

                elif content_block.type == "tool_use":
                    tool_name = content_block.name

                    if tool_name == "validate_approval_chain":
                        # Check all stages passed
                        if kyc_decision == "PASS" and compliance_risk in ["LOW", "MEDIUM", "HIGH"] and docs_generated and setup_status == "READY":
                            # Check for strategy mismatch
                            if compliance_risk in ["MEDIUM", "HIGH"] and profile_strategy == "AGGRESSIVE":
                                critic_decision = "ESCALATE_FOR_REVIEW"
                                flags.append("RISK_STRATEGY_MISMATCH")
                            else:
                                critic_decision = "CONFIRM_APPROVAL"
                        else:
                            critic_decision = "REJECT"

                    elif tool_name == "detect_inconsistencies":
                        # Check for inconsistencies
                        if compliance_risk in ["MEDIUM", "HIGH"] and profile_strategy == "AGGRESSIVE":
                            inconsistencies.append({
                                "type": "risk_strategy_mismatch",
                                "severity": "medium",
                                "detail": f"Compliance risk is {compliance_risk} but strategy is {profile_strategy}"
                            })
                            if critic_decision != "ESCALATE_FOR_REVIEW":
                                critic_decision = "ESCALATE_FOR_REVIEW"
                                flags.append("INCONSISTENCY_DETECTED")

        if not reasoning:
            if critic_decision == "CONFIRM_APPROVAL":
                reasoning = f"All stages passed. KYC:PASS, Compliance:{compliance_risk}, Profile:{profile_strategy}, Setup:READY. Approval confirmed."
            elif critic_decision == "ESCALATE_FOR_REVIEW":
                reasoning = f"Inconsistency detected between risk ({compliance_risk}) and strategy ({profile_strategy}). Manual review recommended."
            elif critic_decision == "REJECT":
                reasoning = "One or more critical stages failed. Rejection recommended."
            else:
                reasoning = "Chain validation complete."

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "agent": "critic_agent",
            "model": SONNET_MODEL,
            "decision": critic_decision,
            "confidence": 0.95 if critic_decision in ["CONFIRM_APPROVAL", "REJECT"] else 0.80,
            "chain_summary": {
                "kyc": kyc_decision,
                "compliance": compliance_risk,
                "documents": "generated" if docs_generated else "missing",
                "profile": profile_strategy,
                "setup": setup_status
            },
            "flags": flags,
            "inconsistencies": inconsistencies,
            "reasoning": reasoning,
            "duration_ms": duration_ms,
            "client_id": client_data.get("client_id")
        }

        return result

    except Exception as e:
        return {
            "agent": "critic_agent",
            "error": str(e),
            "error_category": "APIError",
            "decision": "ESCALATE_FOR_REVIEW"
        }


if __name__ == "__main__":
    from agents.kyc_agent import run_kyc_agent
    from agents.compliance_agent import run_compliance_agent
    from agents.document_agent import run_document_agent
    from agents.profile_agent import run_profile_agent
    from agents.setup_agent import run_setup_agent
    from tools.mocks import SAMPLE_CLIENTS

    test_client = SAMPLE_CLIENTS[0]
    print("Testing Critic Agent with full chain...")

    all_results = {}
    all_results["kyc_agent"] = run_kyc_agent(test_client)
    all_results["compliance_agent"] = run_compliance_agent(test_client, all_results["kyc_agent"])
    all_results["document_agent"] = run_document_agent(test_client, all_results["compliance_agent"])
    all_results["profile_agent"] = run_profile_agent(test_client, all_results)
    all_results["setup_agent"] = run_setup_agent(test_client, all_results)

    critic_result = run_critic_agent(test_client, all_results)

    print("CRITIC Result:")
    print(json.dumps(critic_result, indent=2))
