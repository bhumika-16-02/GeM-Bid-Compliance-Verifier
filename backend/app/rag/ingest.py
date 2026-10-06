from pathlib import Path


def load_documents(folder: str) -> list[dict]:
    """
    Load text documents from a knowledge-base folder.
    """

    documents = []

    for path in Path(folder).glob("*.txt"):
        text = path.read_text(encoding="utf-8").strip()

        if text:
            documents.append(
                {
                    "source": path.name,
                    "text": text,
                }
            )

    return documents