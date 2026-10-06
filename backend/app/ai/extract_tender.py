import fitz


def extract_tender_text(pdf_bytes: bytes) -> str:
    """
    Extract readable text from an uploaded tender PDF.
    """
    document = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = "\n".join(
        page.get_text()
        for page in document
    )

    document.close()

    return text.strip()