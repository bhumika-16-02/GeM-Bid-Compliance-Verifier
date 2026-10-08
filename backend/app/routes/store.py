"""Simple in-memory store that connects the upload steps to the report step.

Why: /tender/upload and /bidder/upload extract data with AI, and
/report/{bidder_id} needs that same data later. Data lives in memory,
so it is cleared when the server restarts (fine for the demo).
"""
TENDERS: dict[str, dict] = {}
BIDDERS: dict[str, dict] = {}


def next_id(prefix: str, table: dict) -> str:
    return f"{prefix}-{len(table) + 1:03d}"