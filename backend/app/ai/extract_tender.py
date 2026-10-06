import sys

import fitz  # PyMuPDF

from app.ai.llm import ask_json

ALLOWED_TYPES = ["PAN", "GST", "UDYAM", "OEM", "LOCAL_CONTENT", "BLACKLIST", "OTHER"]

SYSTEM = (
    "You are an assistant for government procurement officers. "
    "You read tender documents and list the compliance requirements a bidder must meet. "
    "You answer only with JSON."
)


def read_pdf_text(source):
    """Return all text from a PDF. 'source' is a file path or raw bytes."""
    if isinstance(source, (bytes, bytearray)):
        doc = fitz.open(stream=source, filetype="pdf")
    else:
        doc = fitz.open(source)

    pages = []
    for number, page in enumerate(doc, start=1):
        pages.append(f"[Page {number}]\n{page.get_text()}")
    doc.close()
    return "\n".join(pages)


def build_prompt(text):
    return f"""Read this tender document and extract the title and the compliance requirements.

Return JSON in exactly this shape:
{{
  "title": "short tender title",
  "requirements": [
    {{"text": "requirement in one clear sentence", "type": "PAN", "mandatory": true}}
  ]
}}

Rules:
- "type" must be one of: {", ".join(ALLOWED_TYPES)}.
- Use OTHER only if no listed type fits.
- Only include requirements about the bidder's eligibility or documents.
  Skip delivery, payment and other commercial terms.
- "mandatory" is true unless the tender clearly says the requirement is optional.
- Do not invent requirements that are not in the text.

TENDER TEXT:
{text}
"""


def extract_tender(source, tender_id="T-001"):
    """PDF (path or bytes) -> dict in the shape of the API contract."""
    text = read_pdf_text(source)
    if not text.strip():
        raise ValueError("No text found in this PDF. It may be a scanned image.")

    raw = ask_json(build_prompt(text), system=SYSTEM)

    # Don't trust the AI blindly: clean and fix its answer.
    requirements = []
    for index, item in enumerate(raw.get("requirements", []), start=1):
        req_type = str(item.get("type", "OTHER")).upper()
        if req_type not in ALLOWED_TYPES:
            req_type = "OTHER"
        requirements.append(
            {
                "id": f"R{index}",
                "text": str(item.get("text", "")).strip(),
                "type": req_type,
                "mandatory": bool(item.get("mandatory", True)),
            }
        )

    return {
        "tender_id": tender_id,
        "title": raw.get("title", "Untitled tender"),
        "requirements": requirements,
    }


if __name__ == "__main__":
    import json

    path = sys.argv[1] if len(sys.argv) > 1 else "../data/demo_docs/tender.pdf"
    print(json.dumps(extract_tender(path), indent=2))