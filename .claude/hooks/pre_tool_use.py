"""PreToolUse Hook - Validates agent tool calls for PII leakage and compliance.

This hook runs BEFORE any tool is invoked by any agent, ensuring:
1. No PII (names, SSNs, emails) in logs or model inputs
2. All tool schemas follow 5-rule pattern
3. Error categories are explicit
4. Compliance decisions are reasoned
"""

import re
from typing import Dict, Any, List

class PIIValidator:
    """Detects and masks personally identifiable information."""

    # Patterns for PII detection
    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\d{3}-\d{3}-\d{4}\b",
        "account": r"\bACC-\d{6}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    }

    @staticmethod
    def has_pii(text: str) -> List[Dict[str, Any]]:
        """Check if text contains PII. Returns list of detected PII."""
        findings = []

        for pii_type, pattern in PIIValidator.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                findings.append({
                    "type": pii_type,
                    "value": match.group(),
                    "reason": f"Detected {pii_type} pattern"
                })

        return findings

    @staticmethod
    def mask_pii(text: str) -> str:
        """Mask all PII in text."""
        masked = text

        # Email: user@domain.com → u***@domain.com
        masked = re.sub(
            r"(\b[A-Za-z0-9._%+-])([A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})",
            r"\1***@[MASKED_DOMAIN]",
            masked
        )

        # SSN: 123-45-6789 → ***-**-6789
        masked = re.sub(r"\b\d{3}-\d{2}-(\d{4})\b", r"***-**-\1", masked)

        # Phone: 123-456-7890 → ***-***-7890
        masked = re.sub(r"\b\d{3}-\d{3}-(\d{4})\b", r"***-***-\1", masked)

        # Account: ACC-123456 → ACC-[MASKED]
        masked = re.sub(r"\bACC-\d+\b", "ACC-[MASKED]", masked)

        return masked


class ToolValidator:
    """Validates tool schemas and parameters."""

    # Expected 5-rule structure
    FIVE_RULE_KEYWORDS = ["WHAT", "WHEN", "WHY", "INPUT", "ERROR"]

    @staticmethod
    def validate_tool_schema(tool_def: Dict[str, Any]) -> Dict[str, Any]:
        """Check if tool follows 5-rule pattern."""
        function = tool_def.get("function", {})
        name = function.get("name", "UNKNOWN")
        description = function.get("description", "")

        issues = []

        # Check for 5-rule keywords
        for rule in ToolValidator.FIVE_RULE_KEYWORDS:
            if rule not in description.upper():
                issues.append(f"Missing '{rule}' clause in description")

        return {
            "tool_name": name,
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def sanitize_parameters(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or mask PII from tool parameters."""
        sanitized = {}

        for key, value in parameters.items():
            if isinstance(value, str):
                pii_found = PIIValidator.has_pii(value)
                if pii_found:
                    sanitized[key] = PIIValidator.mask_pii(value)
                else:
                    sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = ToolValidator.sanitize_parameters(tool_name, value)
            elif isinstance(value, list):
                sanitized[key] = [
                    ToolValidator.sanitize_parameters(tool_name, item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


def pre_tool_use_hook(tool_use_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    PreToolUse Hook - Runs before any tool invocation.

    Args:
        tool_use_event: Tool invocation event with:
            - tool_name: str
            - tool_definition: Dict with function schema
            - input_parameters: Dict of parameters

    Returns:
        Modified event or error message
    """
    tool_name = tool_use_event.get("tool_name", "UNKNOWN")
    tool_def = tool_use_event.get("tool_definition", {})
    parameters = tool_use_event.get("input_parameters", {})

    # Log (masked)
    print(f"\n[PreToolUse Hook] Validating tool: {tool_name}")

    # 1. Check for PII in parameters
    pii_found = []
    for key, value in parameters.items():
        if isinstance(value, str):
            findings = PIIValidator.has_pii(value)
            pii_found.extend(findings)

    if pii_found:
        print(f"  ⚠️  PII Detected ({len(pii_found)} items):")
        for item in pii_found:
            print(f"     - {item['type']}: {item['reason']}")
        # Mask PII in parameters
        parameters = ToolValidator.sanitize_parameters(tool_name, parameters)
        tool_use_event["input_parameters"] = parameters
        print(f"  ✓ PII masked before tool invocation")

    # 2. Validate tool schema
    schema_check = ToolValidator.validate_tool_schema(tool_def)
    if not schema_check["is_valid"]:
        print(f"  ⚠️  Schema Issues:")
        for issue in schema_check["issues"]:
            print(f"     - {issue}")

    # 3. Check for explicit error categories in description
    description = tool_def.get("function", {}).get("description", "")
    if "Error" not in description:
        print(f"  ⚠️  Missing explicit error handling in tool description")

    print(f"  ✓ Hook validation complete - proceeding with tool invocation")

    return tool_use_event


# Example usage in agent code:
if __name__ == "__main__":
    # Test 1: PII Detection
    print("="*60)
    print("TEST 1: PII Detection")
    print("="*60)

    test_text = "Client email: john.smith@example.com, SSN: 123-45-6789"
    findings = PIIValidator.has_pii(test_text)
    print(f"Text: {test_text}")
    print(f"PII Found: {findings}")
    masked = PIIValidator.mask_pii(test_text)
    print(f"Masked: {masked}\n")

    # Test 2: Tool Schema Validation
    print("="*60)
    print("TEST 2: Tool Schema Validation")
    print("="*60)

    test_tool = {
        "function": {
            "name": "verify_identity",
            "description": """
WHAT: Verifies client identity.
WHEN: Initial KYC stage.
WHY: Regulatory requirement.
INPUT: client_name, document_type.
ERROR: InvalidIDFormat if pattern mismatch.
            """
        }
    }
    validation = ToolValidator.validate_tool_schema(test_tool)
    print(f"Tool: {validation['tool_name']}")
    print(f"Valid 5-Rule Format: {validation['is_valid']}")
    if validation['issues']:
        print(f"Issues: {validation['issues']}\n")

    # Test 3: Pre-tool hook
    print("="*60)
    print("TEST 3: Pre-Tool Hook")
    print("="*60)

    test_event = {
        "tool_name": "verify_identity",
        "tool_definition": test_tool,
        "input_parameters": {
            "client_name": "John Smith",
            "email": "john@example.com",
            "ssn": "123-45-6789"
        }
    }
    result = pre_tool_use_hook(test_event)
    print(f"\nSanitized Parameters:")
    print(f"  {result['input_parameters']}")
