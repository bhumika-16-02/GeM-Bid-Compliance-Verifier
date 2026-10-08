from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.ai.extract_bidder import extract_bidder
from app.store import BIDDERS, next_id

router = APIRouter(prefix="/bidder", tags=["Bidder"])


class BidderFieldsUpdate(BaseModel):
    documents: list[dict]


@router.post("/upload")
async def upload_bidder_documents(
    tender_id: str = Form(...),
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

    to_extract = []
    for doc_type, file in files.items():
        if file is not None:
            to_extract.append((file.filename, await file.read()))

    if not to_extract:
        raise HTTPException(status_code=400, detail="Upload at least one document")

    bidder_id = next_id("B", BIDDERS)
    try:
        bidder = extract_bidder(to_extract, bidder_id=bidder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    bidder["tender_id"] = tender_id
    BIDDERS[bidder_id] = bidder
    return bidder


@router.put("/{bidder_id}/fields")
async def update_bidder_fields(bidder_id: str, data: BidderFieldsUpdate):
    """Save the officer's corrections so the report uses the corrected values."""
    bidder = BIDDERS.get(bidder_id)
    if bidder is None:
        raise HTTPException(status_code=404, detail="Bidder not found")

    bidder["documents"] = data.documents
    return {"ok": True, "bidder_id": bidder_id, "documents": bidder["documents"]}