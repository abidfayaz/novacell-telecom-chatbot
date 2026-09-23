"""Ingest resolved support tickets into the `tickets` Chroma collection.

One ticket row -> one vector document (FR-15). Only resolved tickets are
embedded, since their value is the proven resolution. Re-runs are idempotent
(FR-17), so support ops can seed new tickets and re-run (US-07).
"""

from __future__ import annotations

import sqlite3

from langchain_core.documents import Document

from config import COLLECTION_TICKETS, TICKETS_DB
from vectorstore import get_vectorstore, reset_collection


def load_ticket_documents() -> list[Document]:
    docs: list[Document] = []
    conn = sqlite3.connect(TICKETS_DB)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT ticket_id, category, issue_type, description, resolution, status
            FROM tickets
            WHERE LOWER(status) = 'resolved'
            """
        ).fetchall()
    finally:
        conn.close()

    for row in rows:
        issue_type = (row["issue_type"] or "").strip()
        description = (row["description"] or "").strip()
        resolution = (row["resolution"] or "").strip()
        if not resolution:
            continue
        content = (
            f"Issue: {issue_type}\n"
            f"Description: {description}\n"
            f"Resolution: {resolution}"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": "tickets",
                    "ticket_id": row["ticket_id"],
                    "category": (row["category"] or "").strip(),
                    "issue_type": issue_type,
                },
            )
        )
    return docs


def ingest() -> int:
    docs = load_ticket_documents()
    if not docs:
        print("No resolved tickets found — nothing to ingest.")
        return 0

    reset_collection(COLLECTION_TICKETS)
    store = get_vectorstore(COLLECTION_TICKETS)
    ids = [
        f"ticket-{doc.metadata.get('ticket_id') or i}"
        for i, doc in enumerate(docs)
    ]
    store.add_documents(docs, ids=ids)
    print(f"Ingested {len(docs)} resolved tickets into '{COLLECTION_TICKETS}'.")
    return len(docs)


if __name__ == "__main__":
    ingest()
