"""Tool schemas following 5-rule pattern: What/When/Why/Input/Error."""

TOOL_SCHEMAS = {
    "verify_identity": {
        "type": "function",
        "function": {
            "name": "verify_identity",
            "description": """
WHAT: Verifies client identity against provided documents.
WHEN: First step in KYC onboarding process.
WHY: Regulatory requirement to confirm applicant identity before account opening.
INPUT: client_name (string), document_type (string), id_number (string).
ERROR: Returns InvalidIDFormat if ID doesn't match expected pattern; DocumentMissing if required doc not provided.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {"type": "string", "description": "Full name of client"},
                    "document_type": {"type": "string", "enum": ["passport", "license", "id_card"]},
                    "id_number": {"type": "string", "description": "Document ID number"}
                },
                "required": ["client_name", "document_type", "id_number"]
            }
        }
    },

    "validate_required_documents": {
        "type": "function",
        "function": {
            "name": "validate_required_documents",
            "description": """
WHAT: Validates that all required onboarding documents have been provided.
WHEN: After initial identity verification in KYC stage.
WHY: Ensures complete documentation for audit trail and regulatory compliance.
INPUT: provided_documents (array of strings: passport, tax_return, proof_of_income, etc.).
ERROR: Returns InsufficientDocuments if required docs missing; InvalidDocumentType if unknown doc type.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "provided_documents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of documents provided by client"
                    }
                },
                "required": ["provided_documents"]
            }
        }
    },

    "sanctions_check": {
        "type": "function",
        "function": {
            "name": "sanctions_check",
            "description": """
WHAT: Screens client against sanctions lists (OFAC, UN, EU, etc.).
WHEN: Compliance check stage - must run before any account provisioning.
WHY: Anti-money laundering (AML) regulatory requirement; failure is automatic rejection.
INPUT: client_name (string), email (string), country (string).
ERROR: Returns SanctionsMatch if client found on list (non-recoverable); DatabaseError if lookup fails.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {"type": "string"},
                    "email": {"type": "string"},
                    "country": {"type": "string", "description": "Country of residence"}
                },
                "required": ["client_name", "email"]
            }
        }
    },

    "assess_compliance_risk": {
        "type": "function",
        "function": {
            "name": "assess_compliance_risk",
            "description": """
WHAT: Calculates compliance risk category (LOW, MEDIUM, HIGH, BLOCKED) for client.
WHEN: After identity and sanctions checks pass.
WHY: Determines approval pathway and triggers enhanced due diligence if needed.
INPUT: income (number), net_worth (number), investment_experience (string), flags (array).
ERROR: Returns InvalidIncome if negative; MissingData if required fields absent.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "income": {"type": "number", "description": "Annual income in USD"},
                    "net_worth": {"type": "number", "description": "Net worth in USD"},
                    "investment_experience": {"type": "string", "enum": ["none", "1-3 years", "3-5 years", "5+ years"]},
                    "flags": {"type": "array", "items": {"type": "string"}, "description": "Risk flags from prior checks"}
                },
                "required": ["income", "net_worth", "investment_experience"]
            }
        }
    },

    "generate_onboarding_documents": {
        "type": "function",
        "function": {
            "name": "generate_onboarding_documents",
            "description": """
WHAT: Generates onboarding legal documents (contracts, disclosures, forms).
WHEN: After compliance approval, before account setup.
WHY: Create audit trail of client acknowledgment and regulatory disclosures.
INPUT: client_id (string), risk_category (string), document_types (array).
ERROR: Returns UnknownDocType if requesting invalid document; GenerationError if template missing.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "risk_category": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                    "document_types": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["wealth_agreement", "risk_disclosure", "aml_certification"]}
                    }
                },
                "required": ["client_id", "risk_category", "document_types"]
            }
        }
    },

    "assess_risk_tolerance": {
        "type": "function",
        "function": {
            "name": "assess_risk_tolerance",
            "description": """
WHAT: Analyzes client's stated risk tolerance and investment profile.
WHEN: Financial profile stage - after documents and compliance approval.
WHY: Determine appropriate investment strategy and asset allocation.
INPUT: income (number), experience (string), time_horizon (string), risk_questionnaire_score (number).
ERROR: Returns InvalidScore if questionnaire_score outside 0-100; IncompleteProfile if missing inputs.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "income": {"type": "number"},
                    "experience": {"type": "string"},
                    "time_horizon": {"type": "string", "enum": ["short", "medium", "long"]},
                    "risk_questionnaire_score": {"type": "number", "minimum": 0, "maximum": 100}
                },
                "required": ["income", "experience", "time_horizon", "risk_questionnaire_score"]
            }
        }
    },

    "recommend_investment_strategy": {
        "type": "function",
        "function": {
            "name": "recommend_investment_strategy",
            "description": """
WHAT: Recommends portfolio strategy (CONSERVATIVE, MODERATE, AGGRESSIVE) based on profile.
WHEN: Financial profile stage - after risk tolerance assessment.
WHY: Provide personalized investment guidance aligned with client goals and risk profile.
INPUT: risk_tolerance (string), time_horizon (string), goals (array).
ERROR: Returns UnknownTolerance if invalid risk level; IncompletProfile if missing data.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_tolerance": {"type": "string", "enum": ["conservative", "moderate", "aggressive"]},
                    "time_horizon": {"type": "string"},
                    "goals": {"type": "array", "items": {"type": "string"}, "description": "Investment goals"}
                },
                "required": ["risk_tolerance", "time_horizon"]
            }
        }
    },

    "create_account": {
        "type": "function",
        "function": {
            "name": "create_account",
            "description": """
WHAT: Provisions new investment account in system.
WHEN: Account setup stage - only after all approvals complete.
WHY: Formally register client in platform and enable trading/investments.
INPUT: client_id (string), account_type (string), initial_deposit (number).
ERROR: Returns AccountExists if client already has account; DatabaseError if provisioning fails.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "account_type": {"type": "string", "enum": ["individual", "joint", "trust"]},
                    "initial_deposit": {"type": "number", "default": 0}
                },
                "required": ["client_id", "account_type"]
            }
        }
    },

    "schedule_advisor_meeting": {
        "type": "function",
        "function": {
            "name": "schedule_advisor_meeting",
            "description": """
WHAT: Schedule initial consultation with wealth advisor.
WHEN: Account setup stage - after account provisioning.
WHY: Establish relationship and personalized service plan.
INPUT: client_id (string), preferred_date_range (string).
ERROR: Returns NoAvailability if no slots open; InvalidDateRange if dates invalid.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "preferred_date_range": {"type": "string", "description": "e.g., 'next 2 weeks'"}
                },
                "required": ["client_id"]
            }
        }
    },

    "validate_approval_chain": {
        "type": "function",
        "function": {
            "name": "validate_approval_chain",
            "description": """
WHAT: Meta-validation of entire onboarding decision chain (CRITIC AGENT).
WHEN: Final stage - after all 5 specialist agents complete.
WHY: Catch hallucinations, detect inconsistencies, implement "4-eyes principle" for approvals.
INPUT: kyc_result (string), compliance_risk (string), profile_strategy (string), setup_status (string).
ERROR: Returns ValidationFailed if chain is inconsistent; returns ESCALATE_FOR_REVIEW recommendation.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "kyc_result": {"type": "string", "enum": ["PASS", "FAIL"]},
                    "compliance_risk": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "BLOCKED"]},
                    "profile_strategy": {"type": "string", "enum": ["CONSERVATIVE", "MODERATE", "AGGRESSIVE"]},
                    "setup_status": {"type": "string", "enum": ["READY", "PENDING", "ERROR"]},
                    "documents_generated": {"type": "boolean"}
                },
                "required": ["kyc_result", "compliance_risk", "profile_strategy", "setup_status"]
            }
        }
    },

    "detect_inconsistencies": {
        "type": "function",
        "function": {
            "name": "detect_inconsistencies",
            "description": """
WHAT: Identify contradictions between compliance risk and financial strategy (CRITIC AGENT).
WHEN: Critic stage validation.
WHY: Flag misalignments (e.g., MEDIUM_RISK with AGGRESSIVE strategy) for manual review.
INPUT: compliance_risk (string), profile_strategy (string).
ERROR: Returns no error; outputs array of detected inconsistencies (may be empty).
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "compliance_risk": {"type": "string"},
                    "profile_strategy": {"type": "string"},
                    "income": {"type": "number", "description": "Client income for context"}
                },
                "required": ["compliance_risk", "profile_strategy"]
            }
        }
    }
}

def get_tool_schema(tool_name: str):
    """Retrieve specific tool schema."""
    return TOOL_SCHEMAS.get(tool_name)

def get_all_tools():
    """Get all tool schemas for agent initialization."""
    return list(TOOL_SCHEMAS.values())
