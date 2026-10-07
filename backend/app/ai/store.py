"""In-memory store for the prototype: the latest tender and every uploaded bidder.
Data is lost when the server restarts."""

_tenders = {}
_bidders = {}
_latest_tender_id = None


def save_tender(tender):
    global _latest_tender_id
    _tenders[tender["tender_id"]] = tender
    _latest_tender_id = tender["tender_id"]
    return tender


def get_tender(tender_id=None):
    return _tenders.get(tender_id or _latest_tender_id)


def next_bidder_id():
    return f"B-{len(_bidders) + 1:03d}"


def save_bidder(bidder):
    _bidders[bidder["bidder_id"]] = bidder
    return bidder


def get_bidder(bidder_id):
    return _bidders.get(bidder_id)


def update_documents(bidder_id, documents):
    bidder = _bidders.get(bidder_id)
    if not bidder:
        return None
    bidder["documents"] = documents
    return bidder