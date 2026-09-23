"""Central configuration for the RAG Telecom Customer Care Chatbot.

All tunable knobs (paths, model names, retrieval depth) live here so that the
ingest scripts, retriever, chain, CLI, and Streamlit UI share one source of
truth (NFR-06: extensibility).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a local .env file if present (NFR-03: no secrets in code).
load_dotenv()

# --- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"          # source knowledge (faq.csv, tickets.db, pdf)
CHROMA_DIR = str(BASE_DIR / "chroma_store")  # persisted vector store (NFR-05)

FAQ_CSV = DATA_DIR / "faq.csv"
TICKETS_DB = DATA_DIR / "tickets.db"
GUIDE_PDF = DATA_DIR / "telecom_guide.pdf"
PLANS_JSON = DATA_DIR / "plans.json"

# --- Collections -----------------------------------------------------------
# Registry of vector collections. Adding a new knowledge source means writing a
# new ingest_*.py and registering its collection name here (NFR-06).
COLLECTION_FAQ = "faq"
COLLECTION_TICKETS = "tickets"
COLLECTION_GUIDES = "guides"
COLLECTION_PLANS = "plans"

# Collections the retriever fans out across, with a human-readable source label
# that gets injected into the prompt context (FR-08).
RETRIEVAL_COLLECTIONS: dict[str, str] = {
    COLLECTION_FAQ: "FAQ",
    COLLECTION_TICKETS: "TICKETS",
    COLLECTION_GUIDES: "GUIDES",
    COLLECTION_PLANS: "PLANS",
}

# --- Embeddings (local, no external API) -----------------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # FR-09, NFR-02

# --- Retrieval -------------------------------------------------------------
TOP_K = 3  # FR-07: top-3 per collection -> 9 docs total across 3 collections

# --- PDF chunking ----------------------------------------------------------
CHUNK_SIZE = 600       # FR-16
CHUNK_OVERLAP = 100    # FR-16

# --- LLM (Groq) ------------------------------------------------------------
LLM_MODEL = "llama-3.3-70b-versatile"  # FR-13
LLM_TEMPERATURE = 0           # FR-12: deterministic, factual
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Escalation copy reused by the prompt and CLI/UI surfaces (FR-11).
ESCALATION_MESSAGE = (
    "I don't have enough verified information to answer that confidently. "
    "Please call 611 or use the MyTelecom app for further help."
)
