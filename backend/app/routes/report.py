from fastapi import APIRouter, HTTPException

from app.ai.pipeline import full_report
from app.store import BIDDERS, TENDERS

router = APIRouter(tags=["Report"])


@router.get("/report/{bidder_id}")
def get_report(bidder_id: str):
    bidder = BIDDERS.get(bidder_id)
    if bidder is None:
        raise HTTPException(status_code=404, detail="Bidder not found")

    tender = TENDERS.get(bidder.get("tender_id"))
    if tender is None:
        tender = {"tender_id": bidder.get("tender_id"), "requirements": []}

    return full_report(bidder, tender)
