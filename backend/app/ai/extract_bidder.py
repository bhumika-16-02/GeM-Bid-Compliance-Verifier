import json
import os
import re
import sys
from datetime import datetime

from app.ai.extract_tender import read_pdf_text
from app.ai.llm import ask_json

# For each document type: which fields we want, and what KIND of value each is.
DOC_FIELDS = {
    "PAN": {"pan_number": "pan", "name": "text"},
    "GST": {"gstin": "gstin", "legal_name": "text", "address": "text", "valid_till": "date"},
    "UDYAM": {"udyam_number": "udyam", "enterprise_name": "text", "category": "text", "address": "text"},
    "OEM": {"oem_name": "text", "bidder_name": "text", "authorized_for": "text", "valid_till": "date"},
    "LOCAL_CONTENT": {"bidder_name": "text", "local_content_percent": "percent"},
}

PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
UDYAM_RE = re.compile(r"^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$")

SYSTEM = (
    "You are an assistant for government procurement officers. "
    "You read bidder documents and extract fields exactly as written. "
    "You answer only with JSON."
)


def build_prompt(text, doc_type_hint):
    spec = "\n".join(
        f'- {t}: fields {", ".join(fields)}' for t, fields in DOC_FIELDS.items()
    )
    if doc_type_hint:
        task = f"This document is of type {doc_type_hint}."
    else:
        task = f"First decide the document type. It must be one of: {', '.join(DOC_FIELDS)}, OTHER."
    return f"""{task}
Then extract the fields for that type.

Fields per type:
{spec}

Return JSON in exactly this shape:
{{"doc_type": "GST", "fields": {{"field_name": "value"}}}}

Rules:
- Copy values exactly as written in the document.
- Write dates as YYYY-MM-DD.
- For local_content_percent give only the number, for example "42".
- If a field is not in the document, use null. Never guess or invent.

DOCUMENT TEXT:
{text}
"""


def normalize(kind, value):
    if value is None:
        return None
    value = str(value).strip()
    if not value or value.lower() in ("null", "none", "n/a"):
        return None
    if kind in ("pan", "gstin", "udyam"):
        return re.sub(r"\s+", "", value).upper()
    if kind == "percent":
        return re.sub(r"[^0-9.]", "", value) or None
    return re.sub(r"\s+", " ", value)


def verify(kind, value, text):
    """Check a value with plain Python: right format AND really present in the text."""
    if not value:
        return False
    squashed = re.sub(r"\s+", "", text).upper()
    if kind == "pan":
        return bool(PAN_RE.match(value)) and value in squashed
    if kind == "gstin":
        return bool(GSTIN_RE.match(value)) and value in squashed
    if kind == "udyam":
        return bool(UDYAM_RE.match(value)) and value in squashed
    if kind == "date":
        try:
            d = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return False
        forms = ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d")
        return any(d.strftime(f) in text for f in forms)
    if kind == "percent":
        return re.fullmatch(r"[0-9]{1,3}(\.[0-9]+)?", value) is not None and value in text
    # plain text
    flat_text = re.sub(r"\s+", " ", text).lower()
    return value.lower() in flat_text


def extract_document(source, source_file, doc_type_hint=None):
    """One PDF -> one entry for the 'documents' list in the API contract."""
    text = read_pdf_text(source)
    if not text.strip():
        return {"doc_type": doc_type_hint or "OTHER", "source_file": source_file,
                "confidence": 0.0, "fields": {}}

    raw = ask_json(build_prompt(text, doc_type_hint), system=SYSTEM)

    doc_type = doc_type_hint or str(raw.get("doc_type", "OTHER")).upper()
    if doc_type not in DOC_FIELDS:
        return {"doc_type": "OTHER", "source_file": source_file,
                "confidence": 0.0, "fields": {}}

    raw_fields = raw.get("fields", {}) or {}
    fields = {}
    verified = 0
    for name, kind in DOC_FIELDS[doc_type].items():
        value = normalize(kind, raw_fields.get(name))
        fields[name] = value
        if verify(kind, value, text):
            verified += 1

    confidence = round(verified / len(DOC_FIELDS[doc_type]), 2)
    return {"doc_type": doc_type, "source_file": source_file,
            "confidence": confidence, "fields": fields}

def build_batch_prompt(items):
    """items: list of (file_name, text). One prompt for all documents."""
    spec = "\n".join(
        f'- {t}: fields {", ".join(fields)}' for t, fields in DOC_FIELDS.items()
    )
    docs = "\n\n".join(f"=== FILE: {name} ===\n{text}" for name, text in items)
    return f"""Below are {len(items)} bidder documents. For EACH one, decide the document type
(one of: {', '.join(DOC_FIELDS)}, OTHER) and extract the fields for that type.

Fields per type:
{spec}

Return JSON in exactly this shape:
{{"documents": [{{"source_file": "gst.pdf", "doc_type": "GST", "fields": {{"field_name": "value"}}}}]}}

Rules:
- Give exactly one entry per file. Copy source_file exactly from its FILE heading.
- Copy values exactly as written in that document.
- Write dates as YYYY-MM-DD.
- For local_content_percent give only the number, for example "42".
- If a field is not in the document, use null. Never guess or invent.

DOCUMENTS:
{docs}
"""


def build_entry(source_file, text, entry):
    """Clean and verify one document's result, using our own checks."""
    empty = {"doc_type": "OTHER", "source_file": source_file, "confidence": 0.0, "fields": {}}
    if not text.strip():
        return empty

    doc_type = str(entry.get("doc_type", "OTHER")).upper()
    if doc_type not in DOC_FIELDS:
        return empty

    raw_fields = entry.get("fields", {}) or {}
    fields = {}
    verified = 0
    for name, kind in DOC_FIELDS[doc_type].items():
        value = normalize(kind, raw_fields.get(name))
        fields[name] = value
        if verify(kind, value, text):
            verified += 1

    confidence = round(verified / len(DOC_FIELDS[doc_type]), 2)
    return {"doc_type": doc_type, "source_file": source_file,
            "confidence": confidence, "fields": fields}

def extract_bidder(files, bidder_id="B-001"):
    """files: list of (file_name, path_or_bytes). ONE AI call for all documents."""
    items = [(name, read_pdf_text(src)) for name, src in files]

    raw = ask_json(build_batch_prompt(items), system=SYSTEM)
    by_file = {str(d.get("source_file")): d for d in raw.get("documents", [])}

    documents = [build_entry(name, text, by_file.get(name, {})) for name, text in items]

    # Company name: first one we can find, in this order of trust.
    company = "Unknown bidder"
    for doc_type, field in [("GST", "legal_name"), ("PAN", "name"),
                            ("UDYAM", "enterprise_name"), ("OEM", "bidder_name")]:
        found = next((d["fields"].get(field) for d in documents
                      if d["doc_type"] == doc_type and d["fields"].get(field)), None)
        if found:
            company = found
            break

    return {"bidder_id": bidder_id, "company_name": company, "documents": documents}



if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "../data/demo_docs/abc"
    pdfs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    result = extract_bidder([(f, os.path.join(folder, f)) for f in pdfs])
    print(json.dumps(result, indent=2))