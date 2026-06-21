"""Main orchestrator - Runs complete multi-agent onboarding workflow for sample clients."""

import json
import os
import sys
from datetime import datetime
from agents.kyc_agent import run_kyc_agent
from agents.compliance_agent import run_compliance_agent
from agents.document_agent import run_document_agent
from agents.profile_agent import run_profile_agent
from agents.setup_agent import run_setup_agent
from agents.critic_agent import run_critic_agent
from tools.mocks import SAMPLE_CLIENTS, mask_pii

def run_onboarding_workflow(client_data: dict) -> dict:
    """Run complete 6-agent onboarding workflow for a single client."""
    print(f"\n{'='*70}")
    print(f"ONBOARDING WORKFLOW: {client_data['client_id']} - {client_data['name']}")
    print(f"{'='*70}")

    # Stage 1: KYC Verification (Haiku)
    print("\n[1/6] KYC Verification Agent (Haiku)...")
    kyc_result = run_kyc_agent(client_data)
    print(f"      Result: {kyc_result['decision']} ({kyc_result.get('duration_ms', 0)}ms)")

    # Stage 2: Compliance Check (Sonnet)
    print("[2/6] Compliance Check Agent (Sonnet)...")
    compliance_result = run_compliance_agent(client_data, kyc_result)
    print(f"      Result: {compliance_result['decision']} ({compliance_result.get('duration_ms', 0)}ms)")

    if compliance_result.get("decision") == "BLOCKED":
        print("\n      ⛔ SANCTIONS MATCH DETECTED - AUTOMATIC REJECTION")
        print("      Escalating to manual review and compliance team...")

    # Stage 3: Document Generation (Haiku)
    print("[3/6] Document Generation Agent (Haiku)...")
    document_result = run_document_agent(client_data, compliance_result)
    print(f"      Result: {document_result['decision']} ({document_result.get('duration_ms', 0)}ms)")
    if document_result.get('documents_count'):
        print(f"      Generated {document_result['documents_count']} documents")

    # Stage 4: Financial Profile (Sonnet)
    print("[4/6] Financial Profile Agent (Sonnet)...")
    profile_result = run_profile_agent(client_data, {
        "kyc_agent": kyc_result,
        "compliance_agent": compliance_result,
        "document_agent": document_result
    })
    print(f"      Result: {profile_result['decision']} ({profile_result.get('duration_ms', 0)}ms)")

    # Stage 5: Account Setup (Haiku)
    print("[5/6] Account Setup Agent (Haiku)...")
    setup_result = run_setup_agent(client_data, {
        "kyc_agent": kyc_result,
        "compliance_agent": compliance_result,
        "document_agent": document_result,
        "profile_agent": profile_result
    })
    print(f"      Result: {setup_result['decision']} ({setup_result.get('duration_ms', 0)}ms)")

    # Stage 6: CRITIC Agent (Sonnet) - Final Validation
    print("[6/6] CRITIC Agent (Sonnet) - Final Validation...")
    all_results = {
        "kyc_agent": kyc_result,
        "compliance_agent": compliance_result,
        "document_agent": document_result,
        "profile_agent": profile_result,
        "setup_agent": setup_result
    }
    critic_result = run_critic_agent(client_data, all_results)
    print(f"      Result: {critic_result['decision']} ({critic_result.get('duration_ms', 0)}ms)")
    if critic_result.get('flags'):
        print(f"      Flags: {', '.join(critic_result['flags'])}")

    # Compile final output
    total_duration_ms = sum([
        kyc_result.get('duration_ms', 0),
        compliance_result.get('duration_ms', 0),
        document_result.get('duration_ms', 0),
        profile_result.get('duration_ms', 0),
        setup_result.get('duration_ms', 0),
        critic_result.get('duration_ms', 0)
    ])

    # Determine final status
    if critic_result['decision'] == "CONFIRM_APPROVAL":
        final_status = "APPROVED"
    elif critic_result['decision'] == "ESCALATE_FOR_REVIEW":
        final_status = "REQUIRES_MANUAL_REVIEW"
    elif critic_result['decision'] == "REJECT":
        final_status = "REJECTED"
    else:
        final_status = "UNKNOWN"

    output = {
        "client_id": client_data['client_id'],
        "client_name": mask_pii(client_data['name'], "name"),
        "final_status": final_status,
        "timestamp": datetime.now().isoformat(),
        "agents_executed": [
            {
                "agent": "kyc_agent",
                "model": kyc_result.get('model'),
                "result": kyc_result['decision'],
                "duration_ms": kyc_result.get('duration_ms', 0)
            },
            {
                "agent": "compliance_agent",
                "model": compliance_result.get('model'),
                "result": compliance_result['decision'],
                "flags": compliance_result.get('flags', []),
                "duration_ms": compliance_result.get('duration_ms', 0)
            },
            {
                "agent": "document_agent",
                "model": document_result.get('model'),
                "result": document_result['decision'],
                "count": document_result.get('documents_count', 0),
                "duration_ms": document_result.get('duration_ms', 0)
            },
            {
                "agent": "profile_agent",
                "model": profile_result.get('model'),
                "result": profile_result['decision'],
                "duration_ms": profile_result.get('duration_ms', 0)
            },
            {
                "agent": "setup_agent",
                "model": setup_result.get('model'),
                "result": setup_result['decision'],
                "account_id": setup_result.get('account_id'),
                "duration_ms": setup_result.get('duration_ms', 0)
            },
            {
                "agent": "critic_agent",
                "model": critic_result.get('model'),
                "result": critic_result['decision'],
                "confidence": critic_result.get('confidence'),
                "flags": critic_result.get('flags', []),
                "duration_ms": critic_result.get('duration_ms', 0)
            }
        ],
        "total_duration_ms": total_duration_ms,
        "decision_reasoning": critic_result.get('reasoning'),
        "inconsistencies": critic_result.get('inconsistencies', []),
        "escalation_reason": critic_result.get('reasoning') if final_status == "REQUIRES_MANUAL_REVIEW" else None,
        "artifacts_generated": document_result.get('documents', []) if document_result['decision'] == "GENERATED" else []
    }

    print(f"\n      {'='*66}")
    print(f"      FINAL DECISION: {final_status}")
    print(f"      Total Duration: {total_duration_ms}ms")
    print(f"      Critic Confidence: {critic_result.get('confidence', 0.0):.0%}")
    print(f"      {'='*66}")

    return output


def main():
    """Run onboarding for all sample clients, save outputs."""
    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    print("\n" + "="*70)
    print("CLIENT ONBOARDING ORCHESTRATOR - CAPSTONE PROJECT")
    print("Multi-Agent Workflow with 6-Agent Chain + Critic Validation")
    print("="*70)

    all_outputs = []

    # Process each sample client
    for i, client in enumerate(SAMPLE_CLIENTS):
        try:
            output = run_onboarding_workflow(client)
            all_outputs.append(output)

            # Save individual output
            output_filename = f"outputs/sample_{client['client_id'].lower()}.json"
            with open(output_filename, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"\n[OK] Saved: {output_filename}")

        except Exception as e:
            print(f"\n[ERROR] Error processing {client['client_id']}: {str(e)}")
            all_outputs.append({
                "client_id": client['client_id'],
                "error": str(e),
                "final_status": "ERROR"
            })

    # Save summary
    summary = {
        "workflow": "Client Onboarding Orchestrator",
        "timestamp": datetime.now().isoformat(),
        "clients_processed": len(SAMPLE_CLIENTS),
        "summary": {
            "approved": len([o for o in all_outputs if o.get('final_status') == 'APPROVED']),
            "rejected": len([o for o in all_outputs if o.get('final_status') == 'REJECTED']),
            "requires_review": len([o for o in all_outputs if o.get('final_status') == 'REQUIRES_MANUAL_REVIEW']),
            "errors": len([o for o in all_outputs if o.get('final_status') == 'ERROR'])
        },
        "clients": all_outputs
    }

    with open("outputs/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*70)
    print("WORKFLOW SUMMARY")
    print("="*70)
    print(f"Clients Processed: {summary['summary']['approved'] + summary['summary']['rejected'] + summary['summary']['requires_review']}")
    print(f"  ✓ Approved: {summary['summary']['approved']}")
    print(f"  ✗ Rejected: {summary['summary']['rejected']}")
    print(f"  ⏳ Requires Review: {summary['summary']['requires_review']}")
    print(f"  ⚠️  Errors: {summary['summary']['errors']}")
    print(f"\nOutputs saved to: outputs/")
    print("="*70 + "\n")

    return all_outputs


if __name__ == "__main__":
    main()
