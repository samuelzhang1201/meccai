"""Security analysis tools."""

from meccaai.core.tool_base import tool


@tool(name="prompt_scanner", description="Scan prompts for sensitive data requests")
def prompt_scanner_tool(user_prompt: str) -> dict[str, str | bool]:
    """Scan user prompts for requests involving sensitive data.

    This tool checks whether the user's question contains requests for sensitive
    data such as salary, wages, profit, margin, PII, etc. Only security analysts
    should have access to this tool.

    Args:
        user_prompt: The user's input prompt to scan

    Returns:
        Dictionary with scan results including risk level and detected keywords
    """
    # Define sensitive keywords and patterns
    sensitive_keywords = [
        # Financial data
        "salary",
        "wages",
        "wage",
        "compensation",
        "profit",
        "margin",
        "revenue",
        "income",
        "earnings",
        "bonus",
        "commission",
        "financial",
        "budget",
        "cost",
        # PII (Personally Identifiable Information)
        "ssn",
        "social security",
        "credit card",
        "password",
        "phone number",
        "address",
        "email",
        "personal",
        "private",
        "confidential",
        "birthdate",
        "birth date",
        "driver license",
        "passport",
        "medical",
        "health",
        # Other sensitive data
        "proprietary",
        "trade secret",
        "classified",
        "restricted",
        "internal only",
        "confidential",
        "sensitive",
        "security",
        "authentication",
        "credentials",
    ]

    # Convert prompt to lowercase for case-insensitive matching
    prompt_lower = user_prompt.lower()

    # Check for sensitive keywords
    detected_keywords = []
    for keyword in sensitive_keywords:
        if keyword in prompt_lower:
            detected_keywords.append(keyword)

    # Determine risk level
    if not detected_keywords:
        risk_level = "low"
        alert = False
    elif len(detected_keywords) <= 2:
        risk_level = "medium"
        alert = True
    else:
        risk_level = "high"
        alert = True

    return {
        "risk_level": risk_level,
        "alert": alert,
        "detected_keywords": ", ".join(detected_keywords)
        if detected_keywords
        else "none",
        "recommendation": (
            "Request contains sensitive data keywords. Consider reviewing with security team."
            if alert
            else "No sensitive data keywords detected."
        ),
    }
