"""Document Generation Agent - Onboarding artifacts creation.
Model: claude-3-5-haiku (template-based, straightforward)
Purpose: Generate legal documents, contracts, disclosures, consent forms.
"""

import json
import time
from typing import Dict, Any
from openai import OpenAI
from tools.mocks import generate_mock_client_docs, mask_pii
from tools.schemas import TOOL_SCHEMAS

client = OpenAI()

HAIKU_MODEL = "claude-3-5-haiku-20241022"

DOCUMENT_TOOLS = [
    TOOL_SCHEMAS["generate_onboarding_documents"],
]

DOCUMENT_SYSTEM_PROMPT = """You are a Document Generation Agent.
Your role: Create onboarding legal documents based on client profile and compliance risk.
Model: claude-3-5-haiku (template generation, efficient)

Instructions:
1. Generate appropriate documents based on risk category:
   - LOW: Standard wealth agreement + basic disclosure
   - MEDIUM: Wealth agreement + enhanced risk disclosure + AML certification
   - HIGH: Full suite (wealth agreement + enhanced disclosure + AML cert + PEP certification)
2. All documents should indicate: document_id, type, status (GENERATED), requires_signature
3. Return array of generated documents with metadata

Be systematic and complete.
"""

def run_document_agent(client_data: Dict[str, Any], compliance_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate onboarding documents for a client."""
    start_time = time.time()

    # Only proceed if compliance passed
    if compliance_result.get("decision") not in ["LOW", "MEDIUM", "HIGH"]:
        return {
            "agent": "document_agent",
            "decision": "SKIPPED",
            "reasoning": "Compliance check did not pass - documents not generated",
            "duration_ms": 0,
            "documents": []
        }

    risk_category = compliance_result.get("decision")
    masked_email = mask_pii(client_data.get("email", ""), "email")

    user_message = f"""
Generate onboarding documents for this client:
- Name: {client_data['name']}
- Email: {masked_email}
- Risk Category: {risk_category}
- Client ID: {client_data['client_id']}

Instructions:
1. Call generate_onboarding_documents with risk_category={risk_category}
2. Based on risk level, generate appropriate documents:
   - LOW: ["wealth_agreement", "risk_disclosure"]
   - MEDIUM: ["wealth_agreement", "risk_disclosure", "aml_certification"]
   - HIGH: ["wealth_agreement", "risk_disclosure", "aml_certification"]
3. Return array of document objects with: document_id, type, status, requires_signature
4. Confirm all documents are GENERATED and ready for signature
"""

    try:
        response = client.beta.messages.create(
            model=HAIKU_MODEL,
            max_tokens=1200,
            tools=DOCUMENT_TOOLS,
            system=DOCUMENT_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Process response
        documents = []
        reasoning = None

        for content_block in response.content:
            if hasattr(content_block, 'text'):
                reasoning = content_block.text

            elif content_block.type == "tool_use":
                if content_block.name == "generate_onboarding_documents":
                    # Generate mock documents based on risk category
                    mock_docs = generate_mock_client_docs(client_data)
                    documents = [
                        mock_docs["onboarding_contract"],
                        mock_docs["risk_disclosure"],
                    ]
                    if risk_category in ["MEDIUM", "HIGH"]:
                        documents.append(mock_docs["compliance_forms"])

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "agent": "document_agent",
            "model": HAIKU_MODEL,
            "decision": "GENERATED",
            "documents_count": len(documents),
            "documents": documents,
            "reasoning": reasoning or f"Generated {len(documents)} documents for {risk_category} risk client",
            "duration_ms": duration_ms,
            "client_id": client_data.get("client_id")
        }

        return result

    except Exception as e:
        return {
            "agent": "document_agent",
            "error": str(e),
            "error_category": "APIError",
            "decision": "FAILED",
            "documents": []
        }


if __name__ == "__main__":
    from agents.kyc_agent import run_kyc_agent
    from agents.compliance_agent import run_compliance_agent
    from tools.mocks import SAMPLE_CLIENTS

    test_client = SAMPLE_CLIENTS[0]
    print("Testing Document Agent...")
    kyc_result = run_kyc_agent(test_client)
    compliance_result = run_compliance_agent(test_client, kyc_result)
    doc_result = run_document_agent(test_client, compliance_result)
    print("Document Result:")
    print(json.dumps(doc_result, indent=2))
