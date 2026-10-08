import chromadb
from sentence_transformers import SentenceTransformer

from app.rag.ingest import COLLECTION, DB_DIR, MODEL_NAME

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def retrieve(query, n=3, req_type=None):
    """Find the n rules closest in meaning to 'query'.
    If req_type is given (e.g. 'GST'), search only that type plus GENERAL rules."""
    collection = chromadb.PersistentClient(path=str(DB_DIR)).get_collection(COLLECTION)
    embedding = _get_model().encode([query], normalize_embeddings=True).tolist()

    where = {"type": {"$in": [req_type, "GENERAL"]}} if req_type else None
    result = collection.query(query_embeddings=embedding, n_results=n, where=where)

    rules = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        rules.append(
            {
                "rule_id": result["ids"][0][i],
                "title": meta["title"],
                "text": result["documents"][0][i],
                "source": meta["source"],
                "score": round(1 - result["distances"][0][i], 3),
            }
        )
    return rules

def get_rule(rule_id):
    """Fetch one rule by its exact id (for example 'LC-02'). Returns None if missing."""
    collection = chromadb.PersistentClient(path=str(DB_DIR)).get_collection(COLLECTION)
    result = collection.get(ids=[rule_id])
    if not result["ids"]:
        return None
    meta = result["metadatas"][0]
    return {
        "rule_id": result["ids"][0],
        "title": meta["title"],
        "text": result["documents"][0],
        "source": meta["source"],
    }


if __name__ == "__main__":
    tests = [
        ("Declared local content is 42 percent but the tender needs 50 percent", None),
        ("Does the GSTIN contain the same PAN as the PAN card?", None),
        ("Company name on the Udyam certificate is different from the GST certificate", None),
        ("Is the bidder on the blacklist?", "BLACKLIST"),
    ]
    for query, req_type in tests:
        print("\nQ:", query)
        for r in retrieve(query, n=2, req_type=req_type):
            print(f'  {r["score"]}  {r["rule_id"]}  {r["title"]}  [{r["source"]}]')