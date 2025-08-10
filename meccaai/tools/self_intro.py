"""Self introduction tool for Lumos AI."""

from meccaai.core.tool_base import tool


@tool(name="self_intro", description="Introduce Lumos AI to users")
def self_intro_tool() -> str:
    """Generate a self-introduction for Lumos AI.

    Returns:
        Introduction message for Lumos AI
    """
    introduction_lines = [
        "Hi, I'm Lumos_AI — created by the Mecca Data team.",
        (
            "I'm here to learn and use tools to provide data insights and help "
            "orchestrate the data team's workflow."
        ),
        (
            "I'm not here to replace anyone — my goal is to improve efficiency, "
            "capability, and effectiveness."
        ),
        (
            "I'm happy to take on repetitive and tedious work so my human co-workers "
            "can focus on higher-value tasks."
        ),
        (
            "Right now I've learned basic dbt skills, Snowflake queries, and Tableau, "
            "and I'm continuing to learn other techniques."
        ),
    ]

    return "\n".join(introduction_lines)
