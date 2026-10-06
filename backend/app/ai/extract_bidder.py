import re


def extract_bidder_details(text: str) -> dict:
    """
    Extract basic bidder details from document text.
    """
    upper_text = text.upper()

    pan_match = re.search(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        upper_text,
    )

    gst_match = re.search(
        r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9]Z[0-9]\b",
        upper_text,
    )

    udyam_match = re.search(
        r"\bUDYAM[-A-Z0-9/]+\b",
        upper_text,
    )

    local_content_match = re.search(
        r"(?:LOCAL\s*CONTENT|LOCAL\s*CONTENT\s*PERCENTAGE|LOCAL\s*CONTENT\s*%)"
        r"\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%",
        upper_text,
    )

    return {
        "pan": pan_match.group(0) if pan_match else None,
        "gst": gst_match.group(0) if gst_match else None,
        "udyam": udyam_match.group(0) if udyam_match else None,
        "local_content": (
            float(local_content_match.group(1))
            if local_content_match
            else None
        ),
    }