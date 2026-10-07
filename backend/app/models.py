from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, Session, create_engine


class Tender(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    title: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Bidder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    pan: Optional[str] = None
    gst: Optional[str] = None
    udyam: Optional[str] = None
    oem: Optional[str] = None
    local_content: Optional[float] = None
    blacklist_status: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ComplianceCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bidder_id: int
    requirement: str
    status: str
    score: float = 0
    reason: Optional[str] = None
    evidence: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    details: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

DATABASE_URL = "sqlite:///./gem_compliance.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session