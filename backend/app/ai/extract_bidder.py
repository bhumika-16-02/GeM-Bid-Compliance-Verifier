import re


def extract_bidder_details(text: str) -> dict:
    """
    Extract basic bidder details from document text.
    """

    pan_match = re.search(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        text.upper(),
    )

    gst_match = re.search(
        r"\b[0-9]{2}[A-Z0-9]{5,15}\b",
        text.upper(),
    )

    udyam_match = re.search(
        r"\bUDYAM[-A-Z0-9/]+\b",
        text.upper(),
    )

    return {
        "pan": pan_match.group(0) if pan_match else None,
        "gst": gst_match.group(0) if gst_match else None,
        "udyam": udyam_match.group(0) if udyam_match else None,
    }