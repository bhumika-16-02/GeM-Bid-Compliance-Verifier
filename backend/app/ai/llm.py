def generate_text(prompt: str) -> str:
    """
    Placeholder LLM helper.

    The actual LLM provider can be connected later through
    environment variables without changing the rest of the backend.
    """
    if not prompt.strip():
        return ""

    return prompt.strip()