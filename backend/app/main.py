from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlmodel import Session, delete

from app.models import (
    AuditLog,
    Bidder,
    ComplianceCheck,
    create_db_and_tables,
    get_session,
)
from app.rules.engine import calculate_compliance


app = FastAPI(
    title="GeM Compliance Verification API",
    version="1.0.0",
)


# -----------------------------
# Request models
# -----------------------------

class BidderCreate(BaseModel):
    name: str
    pan: str | None = None
    gst: str | None = None
    udyam: str | None = None
    oem: str | None = None
    local_content: float | None = None
    blacklist_status: bool = False


class ComplianceRequest(BaseModel):
    bidder_id: int


# -----------------------------
# Startup
# -----------------------------

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# -----------------------------
# Basic endpoints
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "GeM Compliance Verification API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# -----------------------------
# Bidder endpoint
# -----------------------------

@app.post("/bidders")
def create_bidder(
    bidder_data: BidderCreate,
    session: Session = Depends(get_session),
):
    bidder = Bidder(
        name=bidder_data.name,
        pan=bidder_data.pan,
        gst=bidder_data.gst,
        udyam=bidder_data.udyam,
        oem=bidder_data.oem,
        local_content=bidder_data.local_content,
        blacklist_status=bidder_data.blacklist_status,
    )

    session.add(bidder)
    session.commit()
    session.refresh(bidder)

    return bidder


# -----------------------------
# Compliance endpoint
# -----------------------------

@app.post("/compliance/check")
def compliance_check(
    request: ComplianceRequest,
    session: Session = Depends(get_session),
):
    bidder = session.get(Bidder, request.bidder_id)

    if not bidder:
        return {
            "error": "Bidder not found"
        }

    result = calculate_compliance(
        pan=bidder.pan,
        gst=bidder.gst,
        udyam=bidder.udyam,
        oem=bidder.oem,
        local_content=bidder.local_content,
        blacklist_status=bidder.blacklist_status,
    )

    # Remove previous compliance checks for this bidder
    session.exec(
        delete(ComplianceCheck).where(
            ComplianceCheck.bidder_id == bidder.id
        )
    )

    # Save each check to the database
    for requirement, passed in result["checks"].items():
        check = ComplianceCheck(
            bidder_id=bidder.id,
            requirement=requirement,
            status="PASS" if passed else "FAIL",
            score=(
                {
                    "PAN": 15,
                    "GST": 20,
                    "Udyam": 15,
                    "OEM": 20,
                    "Local Content": 20,
                    "Blacklist": 10,
                }.get(requirement, 0)
                if passed
                else 0
            ),
            reason=(
                "Requirement satisfied"
                if passed
                else "Requirement failed"
            ),
        )

        session.add(check)

    # Save audit log
    audit = AuditLog(
        action="COMPLIANCE_CHECK",
        details=(
            f"Bidder {bidder.id} checked. "
            f"Score={result['score']}, "
            f"Risk={result['risk']}"
        ),
    )

    session.add(audit)
    session.commit()

    return result


# -----------------------------
# Report endpoint
# -----------------------------

@app.get("/report/{bidder_id}")
def get_report(
    bidder_id: int,
    session: Session = Depends(get_session),
):
    bidder = session.get(Bidder, bidder_id)

    if not bidder:
        return {
            "error": "Bidder not found"
        }

    checks = session.exec(
        __import__("sqlmodel").select(ComplianceCheck).where(
            ComplianceCheck.bidder_id == bidder_id
        )
    ).all()

    return {
        "bidder": bidder,
        "checks": checks,
    }