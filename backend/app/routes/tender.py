import fitz
from fastapi import APIRouter, File, UploadFile


from app.ai.extract_tender import extract_tender
from app.ai.store import save_tender
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

    return save_tender(extract_tender(contents))