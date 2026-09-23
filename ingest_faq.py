"""Ingest FAQ entries into the `faq` Chroma collection.

One CSV row -> one vector document (FR-14). Re-runs are idempotent (FR-17):
the collection is reset and rebuilt from the current CSV each time, so support
ops can edit faq.csv and simply re-run this script (US-06).
"""

from __future__ import annotations

import csv

from langchain_core.documents import Document

from config import COLLECTION_FAQ, FAQ_CSV
from vectorstore import get_vectorstore, reset_collection


def load_faq_documents() -> list[Document]:
    docs: list[Document] = []
    with open(FAQ_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            question = (row.get("question") or "").strip()
            answer = (row.get("answer") or "").strip()
            if not question or not answer:
                continue
            row_id = (row.get("id") or "").strip()
            category = (row.get("category") or "").strip()
            # Embed the question + answer together so retrieval matches on either.
            content = f"Q: {question}\nA: {answer}"
            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": "faq",
                        "id": row_id,
                        "category": category,
                        "question": question,
                    },
                )
            )
    return docs


def ingest() -> int:
    docs = load_faq_documents()
    if not docs:
        print("No FAQ rows found — nothing to ingest.")
        return 0

    reset_collection(COLLECTION_FAQ)
    store = get_vectorstore(COLLECTION_FAQ)
    ids = [f"faq-{i}" for i, _ in enumerate(docs)]
    store.add_documents(docs, ids=ids)
    print(f"Ingested {len(docs)} FAQ entries into '{COLLECTION_FAQ}'.")
    return len(docs)


if __name__ == "__main__":
    ingest()
