import fitz
from fastapi import APIRouter, File, UploadFile


router = APIRouter(prefix="/tender", tags=["Tender"])


@router.post("/upload")
async def upload_tender(file: UploadFile = File(...)):
    contents = await file.read()

    # Read the uploaded PDF so the backend verifies that
    # the uploaded file can actually be processed.
    try:
        document = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join(page.get_text() for page in document)
        document.close()
    except Exception:
        return {
            "error": "Unable to read the uploaded PDF"
        }

    if not text.strip():
        return {
            "error": "The uploaded PDF contains no readable text"
        }

    requirements = [
        {
            "id": "R1",
            "text": "Valid PAN card of the bidder",
            "type": "PAN",
            "mandatory": True,
        },
        {
            "id": "R2",
            "text": "Valid GST registration certificate",
            "type": "GST",
            "mandatory": True,
        },
        {
            "id": "R3",
            "text": "Udyam (MSME) registration certificate",
            "type": "UDYAM",
            "mandatory": True,
        },
        {
            "id": "R4",
            "text": "OEM authorization letter",
            "type": "OEM",
            "mandatory": True,
        },
        {
            "id": "R5",
            "text": "Local content of at least 50%",
            "type": "LOCAL_CONTENT",
            "mandatory": True,
        },
        {
            "id": "R6",
            "text": "Bidder must not be debarred or blacklisted",
            "type": "BLACKLIST",
            "mandatory": True,
        },
    ]

    return {
        "tender_id": "T-001",
        "title": "Supply of 100 Laptops",
        "requirements": requirements,
    }