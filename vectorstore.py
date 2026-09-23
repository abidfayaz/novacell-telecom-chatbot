"""Shared embedding model and Chroma vector-store helpers.

Centralising these means every ingest script and the retriever use the exact
same embedding function and on-disk store (FR-09, NFR-02, NFR-05).
"""

from __future__ import annotations

import functools

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config import CHROMA_DIR, EMBEDDING_MODEL


@functools.lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached local embedding model.

    Cached so the ~90 MB model is loaded into memory only once per process.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


def get_vectorstore(collection_name: str) -> Chroma:
    """Open (or create) a persisted Chroma collection."""
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def reset_collection(collection_name: str) -> None:
    """Drop a collection if it exists so an ingest re-run is idempotent (FR-17).

    Re-ingesting from scratch (rather than upserting) guarantees that rows
    deleted from the source also disappear from the vector store.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(collection_name)
    except Exception:
        # Collection didn't exist yet — nothing to reset.
        pass
