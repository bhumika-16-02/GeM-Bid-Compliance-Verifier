TENDERS: dict[str, dict] = {}
BIDDERS: dict[str, dict] = {}


def next_id(prefix: str, table: dict) -> str:
    return f"{prefix}-{len(table) + 1:03d}"
