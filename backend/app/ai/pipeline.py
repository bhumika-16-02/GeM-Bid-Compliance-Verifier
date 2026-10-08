import json
from pathlib import Path

from app.ai.explain import build_report

DEBARRED_FILE = Path(__file__).resolve().parents[3] / "data" / "mock_debarred.json"


def _field(bidder, doc_type, name):
    for doc in bidder.get("documents", []):
        if doc.get("doc_type") == doc_type:
            return doc.get("fields", {}).get(name)
    return None


def is_debarred(bidder):
    """Simulated check: is the bidder's GSTIN or PAN in data/mock_debarred.json?"""
    try:
        data = json.loads(DEBARRED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return False
    listed = {str(x).strip().upper() for x in data.get("debarred", [])}
    ids = {
        str(_field(bidder, "GST", "gstin") or "").strip().upper(),
        str(_field(bidder, "PAN", "pan_number") or "").strip().upper(),
    }
    ids.discard("")
    return bool(listed & ids)


def engine_inputs(bidder):
    """Bidder JSON -> the keyword arguments of Member B's calculate_compliance()."""
    pct = _field(bidder, "LOCAL_CONTENT", "local_content_percent")
    try:
        pct = float(pct) if pct is not None else None
    except ValueError:
        pct = None
    return {
        "pan": _field(bidder, "PAN", "pan_number"),
        "gst": _field(bidder, "GST", "gstin"),
        "udyam": _field(bidder, "UDYAM", "udyam_number"),
        "oem": _field(bidder, "OEM", "oem_name"),
        "local_content": pct,
        "blacklist_status": is_debarred(bidder),
    }


def full_report(bidder, tender, use_ai=True):
    """bidder JSON + tender JSON -> final report. One call for the whole pipeline."""
    from app.rules.engine import calculate_compliance  # Member B's engine

    result = calculate_compliance(**engine_inputs(bidder))
    return build_report(bidder, tender, result, use_ai=use_ai)


if __name__ == "__main__":
    import os

    from app.ai.extract_bidder import extract_bidder

    folder = "../data/demo_docs/abc"
    pdfs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    bidder = extract_bidder([(f, os.path.join(folder, f)) for f in pdfs])
    print(engine_inputs(bidder))