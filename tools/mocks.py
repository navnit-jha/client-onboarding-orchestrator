"""Mock data and simulated databases for capstone development."""

import random
from typing import Dict, List, Any

# Mock sanctions database
SANCTIONS_DATABASE = {
    "john.terrorist@domain.com": True,
    "jane.pep@domain.com": True,  # PEP = Politically Exposed Person
    "normal.client@domain.com": False,
}

# Mock compliance rules
COMPLIANCE_RULES = {
    "income_thresholds": {
        "high_net_worth": 1000000,  # $1M+
        "ultra_high_net_worth": 5000000,  # $5M+
    },
    "risk_scoring": {
        "sanctions_match": 100,  # Blocking score
        "high_income": 15,  # Adds to risk
        "aggressive_strategy": 10,  # Adds to risk
        "new_investor": 5,  # Minor risk
    },
}

# Sample client profiles
SAMPLE_CLIENTS = [
    {
        "client_id": "CLI001",
        "name": "John Smith",
        "email": "john.smith@example.com",
        "income": 500000,
        "net_worth": 2000000,
        "investment_experience": "5+ years",
        "risk_tolerance": "moderate",
        "documents": ["passport", "tax_return", "proof_of_income"],
        "expected_outcome": "APPROVED",
        "description": "Conservative, established investor, good documentation"
    },
    {
        "client_id": "CLI002",
        "name": "Jane Terrorist",
        "email": "jane.terrorist@example.com",
        "income": 1500000,
        "net_worth": 5000000,
        "investment_experience": "10+ years",
        "risk_tolerance": "aggressive",
        "documents": ["passport", "tax_return"],
        "expected_outcome": "REJECTED",
        "description": "Sanctions match - automatic rejection"
    },
    {
        "client_id": "CLI003",
        "name": "Bob Chen",
        "email": "bob.chen@example.com",
        "income": 5500000,
        "net_worth": 25000000,
        "investment_experience": "3 years",
        "risk_tolerance": "aggressive",
        "documents": ["passport", "bank_statement"],
        "expected_outcome": "REQUIRES_REVIEW",
        "description": "High net worth + aggressive strategy + limited experience - critic flags inconsistency"
    }
]

def mask_pii(value: str, pattern: str = "email") -> str:
    """Mask personally identifiable information for logs."""
    if pattern == "email":
        if "@" in value:
            parts = value.split("@")
            return f"{parts[0][:2]}***@{parts[1][-8:]}"
        return "[MASKED_EMAIL]"
    elif pattern == "name":
        return "[MASKED_NAME]"
    elif pattern == "ssn":
        return "***-**-" + value[-4:] if len(value) >= 4 else "[MASKED_SSN]"
    elif pattern == "account":
        return f"ACC-****-{value[-4:]}" if len(value) >= 4 else "[MASKED_ACC]"
    else:
        return "[MASKED]"


def check_sanctions(email: str, name: str) -> Dict[str, Any]:
    """Check if client is on sanctions list (mock implementation)."""
    is_sanctioned = SANCTIONS_DATABASE.get(email, False)

    return {
        "is_sanctioned": is_sanctioned,
        "match_email": email in SANCTIONS_DATABASE,
        "reasoning": "Exact match in sanctions database" if is_sanctioned else "No match found",
        "database_version": "mock_v1.0"
    }


def assess_risk_score(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate compliance risk score based on client profile."""
    score = 0
    flags = []

    # Check sanctions
    sanctions_result = check_sanctions(client_data.get("email", ""), client_data.get("name", ""))
    if sanctions_result["is_sanctioned"]:
        score += COMPLIANCE_RULES["risk_scoring"]["sanctions_match"]
        flags.append("SANCTIONS_MATCH")
        return {
            "risk_level": "BLOCKED",
            "score": score,
            "flags": flags,
            "reasoning": "Client on sanctions list - automatic block"
        }

    # Check income level
    income = client_data.get("income", 0)
    if income >= COMPLIANCE_RULES["risk_scoring"]["high_net_worth"]:
        score += COMPLIANCE_RULES["risk_scoring"]["high_income"]
        flags.append("HIGH_NET_WORTH")

    # Determine risk level
    if score >= 50:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_level": risk_level,
        "score": score,
        "flags": flags,
        "reasoning": f"Risk assessment complete. Score: {score}, Flags: {', '.join(flags) if flags else 'None'}"
    }


def validate_documents(documents: List[str]) -> Dict[str, Any]:
    """Validate that all required documents are provided."""
    required_docs = {"passport", "tax_return"}
    provided = set(documents)
    missing = required_docs - provided

    return {
        "is_complete": len(missing) == 0,
        "missing_documents": list(missing),
        "provided_documents": list(provided),
        "reasoning": "All required documents provided" if len(missing) == 0 else f"Missing: {', '.join(missing)}"
    }


def generate_mock_client_docs(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock client documents."""
    return {
        "onboarding_contract": {
            "document_id": f"DOC-{random.randint(10000, 99999)}",
            "type": "Wealth Management Agreement",
            "status": "GENERATED",
            "requires_signature": True
        },
        "risk_disclosure": {
            "document_id": f"DOC-{random.randint(10000, 99999)}",
            "type": "Risk Disclosure Statement",
            "status": "GENERATED",
            "requires_signature": True
        },
        "compliance_forms": {
            "w9": "GENERATED",
            "aml_certification": "GENERATED"
        }
    }


def create_mock_account(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create mock account."""
    account_id = f"ACC-{random.randint(100000, 999999)}"

    return {
        "account_id": account_id,
        "client_id": client_data.get("client_id", "UNKNOWN"),
        "status": "ACTIVE",
        "created_at": "2024-06-21T12:00:00Z",
        "first_deposit_amount": 0,
        "advisor_assigned": "Advisor TBD"
    }


def schedule_advisor_meeting(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Schedule advisor meeting (mock)."""
    return {
        "meeting_id": f"MTG-{random.randint(100000, 999999)}",
        "scheduled_date": "2024-07-05",
        "scheduled_time": "10:00 AM",
        "advisor_email": "advisor@wealthmgmt.example.com",
        "meeting_type": "Initial Consultation"
    }


def validate_strategy_alignment(compliance_risk: str, strategy: str) -> Dict[str, Any]:
    """Validate that financial strategy aligns with compliance risk assessment."""
    alignment_matrix = {
        ("LOW", "CONSERVATIVE"): True,
        ("LOW", "MODERATE"): True,
        ("LOW", "AGGRESSIVE"): True,
        ("MEDIUM", "CONSERVATIVE"): True,
        ("MEDIUM", "MODERATE"): True,
        ("MEDIUM", "AGGRESSIVE"): False,  # Critic flags this
        ("HIGH", "AGGRESSIVE"): False,  # Critic flags this
        ("BLOCKED", "ANY"): False,  # Critic blocks this
    }

    key = (compliance_risk, strategy)
    is_aligned = alignment_matrix.get(key, False)

    return {
        "is_aligned": is_aligned,
        "compliance_risk": compliance_risk,
        "strategy": strategy,
        "reasoning": "Risk and strategy are well-aligned" if is_aligned else "CRITIC ALERT: Strategy misaligned with risk profile"
    }


def get_sample_client(index: int = 0) -> Dict[str, Any]:
    """Get sample client by index."""
    if 0 <= index < len(SAMPLE_CLIENTS):
        return SAMPLE_CLIENTS[index]
    return None
