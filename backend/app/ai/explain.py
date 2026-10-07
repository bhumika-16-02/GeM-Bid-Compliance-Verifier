import json
import re
import sys

from app.ai.llm import ask_json
from app.rag.retrieve import get_rule

LOW_CONFIDENCE = 0.9  # below this, a PASS becomes REVIEW

SYSTEM = (
    "You write short, factual summaries of bid compliance results for government "
    "procurement officers. You answer only with JSON."
)

# type -> (rule name in the contract, rule id in the knowledge base, default text)
CHECK_INFO = {
    "PAN": ("PAN_FORMAT", "PAN-01", "Valid PAN card of the bidder"),
    "GST": ("GST_VALID", "GST-01", "Valid GST registration certificate"),
    "UDYAM": ("UDYAM_PRESENT", "UDY-01", "Udyam (MSME) registration certificate"),
    "OEM": ("OEM_PRESENT", "OEM-01", "OEM authorization letter"),
    "LOCAL_CONTENT": ("LOCAL_CONTENT_MIN", "LC-02", "Local content of at least 50%"),
    "BLACKLIST": ("NOT_DEBARRED", "BL-01", "Bidder must not be debarred or blacklisted"),
}
DEFAULT_IDS = {"PAN": "R1", "GST": "R2", "UDYAM": "R3", "OEM": "R4",
               "LOCAL_CONTENT": "R5", "BLACKLIST": "R6"}


# ---------- small helpers ----------

def canon(name):
    """'Udyam' -> 'UDYAM', 'Local Content' -> 'LOCAL_CONTENT'."""
    return str(name).upper().replace(" ", "_")


def get_doc(bidder, doc_type):
    for doc in bidder.get("documents", []):
        if doc.get("doc_type") == doc_type:
            return doc
    return None


def field(bidder, doc_type, name):
    doc = get_doc(bidder, doc_type)
    return (doc or {}).get("fields", {}).get(name)


def cite(rule_id):
    """Exact lookup of a rule for the citation. Never crashes the report."""
    try:
        rule = get_rule(rule_id)
    except Exception:
        return None
    if not rule:
        return None
    return {"rule_id": rule["rule_id"], "title": rule["title"], "source": rule["source"]}


def required_percent(requirement_text):
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", requirement_text or "")
    return match.group(1) if match else "50"


# ---------- per-check status and evidence ----------

def status_for(passed, doc):
    if not passed:
        return "FAIL"
    if doc and doc.get("confidence", 1.0) < LOW_CONFIDENCE:
        return "REVIEW"
    return "PASS"


def evidence_for(t, bidder, passed, requirement_text):
    """Return (evidence sentence, source). Built by code from extracted fields."""
    if t == "BLACKLIST":
        text = ("Not found in the simulated debarment list." if passed
                else "Found in the simulated debarment list.")
        return text, "mock_debarred.json (Simulated)"

    doc = get_doc(bidder, t)
    if not doc:
        return f"No {t} document was uploaded.", "not uploaded"

    f = doc.get("fields", {})
    src = doc.get("source_file", "unknown")
    conf = doc.get("confidence", 0)

    if t == "PAN":
        v = f.get("pan_number")
        text = f"PAN {v} found." if passed else f"PAN missing or invalid (read as: {v})."
    elif t == "GST":
        g, till = f.get("gstin"), f.get("valid_till")
        text = (f"GSTIN {g} found, valid till {till}." if passed
                else f"GSTIN missing or invalid (read as: {g}).")
    elif t == "UDYAM":
        u, cat = f.get("udyam_number"), f.get("category")
        text = (f"Udyam number {u} found, category {cat}." if passed
                else f"Udyam number missing or invalid (read as: {u}).")
    elif t == "OEM":
        o, auth, till = f.get("oem_name"), f.get("authorized_for"), f.get("valid_till")
        text = (f"Authorization from {o} for {auth}, valid till {till}." if passed
                else f"OEM authorization missing or invalid (read as: {o}).")
    elif t == "LOCAL_CONTENT":
        pct, need = f.get("local_content_percent"), required_percent(requirement_text)
        text = (f"Declared local content is {pct}%, meeting the {need}% minimum." if passed
                else f"Declared local content is {pct}%, below the required {need}%.")
    else:
        text = "Checked."

    if passed and conf < LOW_CONFIDENCE:
        text += f" Extraction confidence was only {int(conf * 100)}%, so please verify the original."
    return text, src


# ---------- cross-document checks ----------

def _norm_name(name):
    n = re.sub(r"[^a-z0-9 ]", " ", str(name).lower())
    n = n.replace("private", "pvt").replace("limited", "ltd")
    return re.sub(r"\s+", " ", n).strip()


def cross_checks(bidder):
    findings = []

    pan, gstin = field(bidder, "PAN", "pan_number"), field(bidder, "GST", "gstin")
    if pan and gstin:
        ok = gstin[2:12] == pan
        findings.append({
            "name": "PAN matches the PAN inside GSTIN",
            "status": "PASS" if ok else "REVIEW",
            "evidence": (f"PAN {pan} equals the PAN inside GSTIN {gstin}." if ok
                         else f"PAN {pan} does not match the PAN inside GSTIN {gstin}."),
            "citation": cite("GST-02"),
        })

    names = {}
    for doc_type, fname in [("PAN", "name"), ("GST", "legal_name"), ("UDYAM", "enterprise_name"),
                            ("OEM", "bidder_name"), ("LOCAL_CONTENT", "bidder_name")]:
        value = field(bidder, doc_type, fname)
        if value:
            names[doc_type] = value
    if len(names) >= 2:
        ok = len({_norm_name(v) for v in names.values()}) == 1
        findings.append({
            "name": "Company name is the same on all documents",
            "status": "PASS" if ok else "REVIEW",
            "evidence": ("The company name is consistent across documents." if ok
                         else "Different company names found: " + "; ".join(
                             f"{k}: {v}" for k, v in names.items())),
            "citation": cite("GEN-01"),
        })

    a1, a2 = field(bidder, "GST", "address"), field(bidder, "UDYAM", "address")
    if a1 and a2:
        pins1, pins2 = re.findall(r"\b\d{6}\b", a1), re.findall(r"\b\d{6}\b", a2)
        if pins1 and pins2:
            ok = pins1[-1] == pins2[-1]
        else:
            ok = _norm_name(a1) == _norm_name(a2)
        findings.append({
            "name": "GST and Udyam addresses refer to the same place",
            "status": "PASS" if ok else "REVIEW",
            "evidence": ("The addresses agree." if ok
                         else f"Addresses differ: GST '{a1}' vs Udyam '{a2}'."),
            "citation": cite("GEN-02"),
        })
    return findings


# ---------- summary ----------

def template_summary(checks, cross, risk):
    passed = sum(1 for c in checks if c["status"] == "PASS")
    text = f"{passed} of {len(checks)} requirements passed. Risk level is {risk}."
    flagged = [f'{c["requirement"].rstrip(".")} ({c["status"]})' for c in checks if c["status"] != "PASS"]
    if flagged:
        text += " Needs attention: " + "; ".join(flagged) + "."
    odd = [c["name"] for c in cross if c["status"] != "PASS"]
    if odd:
        text += " Cross-check flags: " + "; ".join(odd) + "."
    return text + " The Procurement Officer makes the final decision."


def ai_summary(checks, cross, score, risk):
    facts = {
        "score": score,
        "risk": risk,
        "checks": [{"requirement": c["requirement"], "status": c["status"],
                    "evidence": c["evidence"]} for c in checks],
        "cross_checks": [{"name": c["name"], "status": c["status"]} for c in cross],
    }
    prompt = f"""Write a short summary (2 to 3 sentences) of this bid compliance result for a procurement officer.
Use ONLY the facts below. Do not change any status, score or number.
Do not accept or reject the bidder; say that the Procurement Officer decides.

Return JSON in exactly this shape: {{"summary": "..."}}

FACTS:
{json.dumps(facts, indent=2, sort_keys=True)}
"""
    raw = ask_json(prompt, system=SYSTEM)
    summary = raw.get("summary") if isinstance(raw, dict) else None
    return summary.strip() if isinstance(summary, str) and summary.strip() else None


# ---------- main entry point ----------

def build_report(bidder, tender, engine_result, use_ai=True):
    """bidder + tender JSON (from our extractors) + Member B's engine result -> report."""
    req_by_type = {r.get("type"): r for r in tender.get("requirements", [])}

    checks = []
    for name, passed in engine_result["checks"].items():
        t = canon(name)
        if t not in CHECK_INFO:
            continue
        rule_name, rule_id, default_text = CHECK_INFO[t]
        req = req_by_type.get(t, {})
        requirement_text = req.get("text", default_text)
        evidence, source = evidence_for(t, bidder, passed, requirement_text)
        checks.append({
            "requirement_id": req.get("id", DEFAULT_IDS[t]),
            "requirement": requirement_text,
            "status": status_for(passed, get_doc(bidder, t)),
            "evidence": evidence,
            "source": source,
            "rule": rule_name,
            "citation": cite(rule_id),
        })

    cross = cross_checks(bidder)
    score, risk = engine_result["score"], engine_result["risk"]

    flagged = any(c["status"] != "PASS" for c in checks) or any(
        c["status"] != "PASS" for c in cross)
    recommendation = "REVIEW" if flagged else "APPROVE"

    summary = None
    if use_ai:
        try:
            summary = ai_summary(checks, cross, score, risk)
        except Exception as e:
            print(f"(AI summary unavailable: {str(e)[:80]}. Using the template.)")
    if not summary:
        summary = template_summary(checks, cross, risk)

    return {
        "bidder_id": bidder.get("bidder_id"),
        "tender_id": tender.get("tender_id"),
        "score": score,
        "risk": risk,
        "recommendation": recommendation,
        "summary": summary,
        "checks": checks,
        "cross_checks": cross,
    }


def explain_compliance(result: dict) -> str:
    """Kept for Member B's code: a one-line explanation of an engine result."""
    score = result.get("score", 0)
    risk = result.get("risk", "UNKNOWN")
    failed_checks = result.get("failed_checks", [])
    if not failed_checks:
        return f"All compliance requirements passed. Score: {score}/100. Risk: {risk}."
    return (f"Compliance score: {score}/100. Risk: {risk}. "
            f"Failed requirements: {', '.join(failed_checks)}.")


if __name__ == "__main__":
    import os

    from app.ai.extract_bidder import extract_bidder
    from app.ai.extract_tender import extract_tender

    use_ai = "--no-ai" not in sys.argv

    tender = extract_tender("../data/demo_docs/tender.pdf")
    folder = "../data/demo_docs/abc"
    pdfs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    bidder = extract_bidder([(f, os.path.join(folder, f)) for f in pdfs])

    # Same shape as Member B's calculate_compliance() output for the golden demo.
    engine = {
        "checks": {"PAN": True, "GST": True, "Udyam": True, "OEM": True,
                   "Local Content": False, "Blacklist": True},
        "score": 80,
        "risk": "MEDIUM",
        "failed_checks": ["Local Content"],
    }
    print(json.dumps(build_report(bidder, tender, engine, use_ai=use_ai), indent=2))