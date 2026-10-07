import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[3]
KB_FILE = ROOT / "data" / "kb" / "rules.json"
DB_DIR = Path(__file__).resolve().parents[2] / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "gem_rules"


def ingest():
    rules = json.loads(KB_FILE.read_text(encoding="utf-8"))

    model = SentenceTransformer(MODEL_NAME)
    texts = [f'{r["title"]}. {r["text"]}' for r in rules]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION)  # start fresh each time
    except Exception:
        pass
    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    collection.add(
        ids=[r["id"] for r in rules],
        embeddings=embeddings,
        documents=[r["text"] for r in rules],
        metadatas=[
            {"title": r["title"], "type": r["type"], "source": r["source"]}
            for r in rules
        ],
    )
    print(f"Ingested {len(rules)} rules into {DB_DIR}")


if __name__ == "__main__":
    ingest()