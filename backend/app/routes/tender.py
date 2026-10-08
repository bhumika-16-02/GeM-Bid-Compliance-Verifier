import fitz
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ai.extract_tender import extract_tender
from app.store import TENDERS, next_id

router = APIRouter(prefix="/tender", tags=["Tender"])


@router.post("/upload")
async def upload_tender(file: UploadFile = File(...)):
    contents = await file.read()

    # Check the PDF can be read before spending an AI call on it.
    try:
        document = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join(page.get_text() for page in document)
        document.close()
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read the uploaded PDF")

    if not text.strip():
        raise HTTPException(
            status_code=400, detail="The uploaded PDF contains no readable text"
        )

    tender_id = next_id("T", TENDERS)
    try:
        tender = extract_tender(contents, tender_id=tender_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    TENDERS[tender_id] = tender
    return tender