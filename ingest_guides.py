"""Ingest the telecom PDF guide into the `guides` Chroma collection.

The PDF is chunked at 600 characters with 100-character overlap before
embedding (FR-16). Re-runs are idempotent (FR-17).
"""

from __future__ import annotations

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_GUIDES, GUIDE_PDF
from vectorstore import get_vectorstore, reset_collection


def load_guide_documents() -> list[Document]:
    pages = PyPDFLoader(str(GUIDE_PDF)).load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(pages)
    for chunk in chunks:
        # Normalise metadata: keep the page number, tag the source.
        chunk.metadata = {
            "source": "guides",
            "page": chunk.metadata.get("page"),
        }
    return chunks


def ingest() -> int:
    docs = load_guide_documents()
    if not docs:
        print("No guide chunks produced — nothing to ingest.")
        return 0

    reset_collection(COLLECTION_GUIDES)
    store = get_vectorstore(COLLECTION_GUIDES)
    ids = [f"guide-{i}" for i, _ in enumerate(docs)]
    store.add_documents(docs, ids=ids)
    print(
        f"Ingested {len(docs)} guide chunks "
        f"({CHUNK_SIZE}-char / {CHUNK_OVERLAP}-overlap) into '{COLLECTION_GUIDES}'."
    )
    return len(docs)


if __name__ == "__main__":
    ingest()
