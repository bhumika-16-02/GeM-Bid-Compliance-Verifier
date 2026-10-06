import fitz
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.ai.extract_bidder import extract_bidder_details


router = APIRouter(prefix="/bidder", tags=["Bidder"])


async def read_pdf(file: UploadFile | None) -> str:
    if file is None:
        return ""

    contents = await file.read()

    try:
        document = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join(page.get_text() for page in document)
        document.close()
        return text.strip()
    except Exception:
        return ""

class BidderFieldsUpdate(BaseModel):
    documents: list[dict]


@router.put("/{bidder_id}/fields")
async def update_bidder_fields(
    bidder_id: str,
    data: BidderFieldsUpdate,
):
    return {
        "ok": True,
        "bidder_id": bidder_id,
        "documents": data.documents,
    }
@router.post("/upload")
async def upload_bidder_documents(
    tender_id: str = File(...),
    PAN: UploadFile | None = File(None),
    GST: UploadFile | None = File(None),
    UDYAM: UploadFile | None = File(None),
    OEM: UploadFile | None = File(None),
    LOCAL_CONTENT: UploadFile | None = File(None),
):
    files = {
        "PAN": PAN,
        "GST": GST,
        "UDYAM": UDYAM,
        "OEM": OEM,
        "LOCAL_CONTENT": LOCAL_CONTENT,
    }

    documents = []

    for doc_type, file in files.items():
        if file is None:
            continue

        text = await read_pdf(file)
        extracted = extract_bidder_details(text)

        fields = {}

        if doc_type == "PAN":
            fields = {
                "pan_number": extracted.get("pan"),
            }

        elif doc_type == "GST":
            fields = {
                "gstin": extracted.get("gst"),
            }

        elif doc_type == "UDYAM":
            fields = {
                "udyam_number": extracted.get("udyam"),
            }
        elif doc_type == "LOCAL_CONTENT":
            fields = {
                "local_content_percent": extracted.get("local_content"),
    }

        documents.append(
            {
                "doc_type": doc_type,
                "source_file": file.filename,
                "confidence": 1.0 if text else 0.0,
                "fields": fields,
            }
        )

    return {
        "bidder_id": "B-001",
        "company_name": "Sunrise Technologies Pvt Ltd",
        "documents": documents,
    }