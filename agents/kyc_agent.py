"""KYC Verification Agent - Identity validation and document collection.
Model: claude-3-5-haiku (fast, cost-efficient)
Purpose: Validate client identity and ensure all required documents provided.
"""

import json
import time
from typing import Dict, Any
from openai import OpenAI
from tools.mocks import validate_documents, mask_pii, SAMPLE_CLIENTS
from tools.schemas import TOOL_SCHEMAS

client = OpenAI()

HAIKU_MODEL = "claude-3-5-haiku-20241022"

KYC_TOOLS = [
    TOOL_SCHEMAS["verify_identity"],
    TOOL_SCHEMAS["validate_required_documents"],
]

KYC_SYSTEM_PROMPT = """You are a KYC (Know Your Customer) Verification Agent.
Your role: Validate client identity and ensure all required documents are provided.
Model: claude-3-5-haiku (fast validation, cost-efficient)

Instructions:
1. Verify the client identity using provided documents
2. Check that all required documents are present (passport, tax_return)
3. Return structured decision: PASS or FAIL
4. If FAIL, list missing documents or identity issues

Always respond with a decision and reasoning. Be strict but fair.
"""

def run_kyc_agent(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run KYC verification for a client."""
    start_time = time.time()

    # Prepare client data for analysis (mask PII in logs)
    masked_email = mask_pii(client_data.get("email", ""), "email")

    user_message = f"""
Verify KYC for this client:
- Name: {client_data['name']}
- Email: {masked_email}
- Documents provided: {', '.join(client_data['documents'])}
- Required: passport, tax_return

1. Call verify_identity to confirm strong identity
2. Call validate_required_documents to check completeness
3. Return structured decision: PASS or FAIL with reasoning
"""

    try:
        response = client.beta.messages.create(
            model=HAIKU_MODEL,
            max_tokens=1024,
            tools=KYC_TOOLS,
            system=KYC_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Process tool calls
        decision = None
        reasoning = None

        for content_block in response.content:
            if hasattr(content_block, 'text'):
                reasoning = content_block.text
            elif content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input

                if tool_name == "verify_identity":
                    decision = "PASS"
                elif tool_name == "validate_required_documents":
                    doc_result = validate_documents(client_data.get("documents", []))
                    decision = "PASS" if doc_result["is_complete"] else "FAIL"
                    reasoning = doc_result["reasoning"]

        if not decision:
            decision = "PASS"

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "agent": "kyc_agent",
            "model": HAIKU_MODEL,
            "decision": decision,
            "reasoning": reasoning or "Documents verified",
            "duration_ms": duration_ms,
            "client_id": client_data.get("client_id"),
            "documents_checked": client_data.get("documents", [])
        }

        return result

    except Exception as e:
        return {
            "agent": "kyc_agent",
            "error": str(e),
            "error_category": "APIError",
            "decision": "FAIL"
        }


if __name__ == "__main__":
    # Test with sample client
    test_client = SAMPLE_CLIENTS[0]
    print("Testing KYC Agent with sample client...")
    print(json.dumps(test_client, indent=2))
    result = run_kyc_agent(test_client)
    print("\nKYC Result:")
    print(json.dumps(result, indent=2))
