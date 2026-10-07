
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.ai.extract_bidder import extract_bidder 


router = APIRouter(prefix="/bidder", tags=["Bidder"])



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

    to_extract = []

    for doc_type, file in files.items():
        if file is not None:
            to_extract.append(
                (file.filename, await file.read())
            )

    return extract_bidder(to_extract)
    