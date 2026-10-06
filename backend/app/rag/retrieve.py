def retrieve_documents(
    documents: list[dict],
    query: str,
) -> list[dict]:
    """
    Retrieve documents containing words from the query.
    """

    query_words = {
        word.lower()
        for word in query.split()
        if word.strip()
    }

    results = []

    for document in documents:
        text = document.get("text", "")
        text_words = {
            word.lower().strip(".,:;()[]")
            for word in text.split()
        }

        if query_words.intersection(text_words):
            results.append(document)

    return results