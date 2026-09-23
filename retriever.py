"""Merged retriever: fans out across all knowledge collections in parallel.

For each query it fetches the top-3 documents from the FAQ, tickets, and guides
collections (FR-06, FR-07) and formats them into a single source-labelled
context block (FR-08) for prompt injection.
"""

from __future__ import annotations

import functools

from langchain_core.documents import Document
from langchain_core.runnables import RunnableParallel

from config import RETRIEVAL_COLLECTIONS, TOP_K
from vectorstore import get_vectorstore


def _build_parallel_retriever() -> RunnableParallel:
    """One retriever per registered collection, invoked concurrently."""
    branches = {
        collection: get_vectorstore(collection).as_retriever(
            search_kwargs={"k": TOP_K}
        )
        for collection in RETRIEVAL_COLLECTIONS
    }
    return RunnableParallel(branches)


@functools.lru_cache(maxsize=1)
def _get_parallel_retriever() -> RunnableParallel:
    """Lazy singleton — built on first query so it always reflects on-disk state."""
    return _build_parallel_retriever()


def _format_documents(results: dict[str, list[Document]]) -> str:
    """Render retrieved docs into a labelled, prompt-ready context string."""
    blocks: list[str] = []
    for collection, label in RETRIEVAL_COLLECTIONS.items():
        docs = results.get(collection, [])
        for doc in docs:
            blocks.append(f"[{label}] {doc.page_content.strip()}")
    return "\n\n".join(blocks)


def retrieve_context(question: str) -> str:
    """Retrieve and format the merged, source-labelled context for a question."""
    results = _get_parallel_retriever().invoke(question)
    return _format_documents(results)
