def explain_compliance(result: dict) -> str:
    """
    Create a simple human-readable explanation of a compliance result.
    """

    score = result.get("score", 0)
    risk = result.get("risk", "UNKNOWN")
    failed_checks = result.get("failed_checks", [])

    if not failed_checks:
        return (
            f"All compliance requirements passed. "
            f"Score: {score}/100. Risk: {risk}."
        )

    failed = ", ".join(failed_checks)

    return (
        f"Compliance score: {score}/100. "
        f"Risk: {risk}. "
        f"Failed requirements: {failed}."
    )