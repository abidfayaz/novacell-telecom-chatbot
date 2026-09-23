# NovaCell Telecom Care Bot

A Retrieval-Augmented Generation (RAG) chatbot that answers Tier-1 telecom
support questions grounded **only** in curated sample knowledge — it never
invents policy, pricing, or steps. Built as an AI PM portfolio project.

**Live demo:** [novacell-telecom-chatbot.streamlit.app](https://novacell-telecom-chatbot.streamlit.app)

> **Portfolio demo.** Uses approved sample telecom knowledge. No access to live
> customer accounts, billing or usage data.

---

## What it does

- Answers connectivity, data, roaming, SIM/eSIM, billing, and plan questions
- Retrieves context from four knowledge sources in parallel before generating
- Refuses to answer when context is insufficient — routes to 611 or the MyTelecom app
- Never uses model memory or general knowledge to fill gaps

## Architecture

```
User question
     │
     ▼
Merged Retriever  (parallel, top-3 per source = 12 docs)
  ├── ChromaDB · faq        FAQ question/answer pairs
  ├── ChromaDB · tickets    resolved support tickets
  ├── ChromaDB · guides     PDF troubleshooting guide chunks
  └── ChromaDB · plans      mobile plans and add-ons
     │  (source-labelled context injected into prompt)
     ▼
ChatPromptTemplate  (telecom persona + strict grounding rules)
     ▼
Llama 3.3 70B on Groq  (temperature=0, deterministic)
     ▼
StrOutputParser → streamed response
```

- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (local, no API cost per query)
- **Vector store:** ChromaDB, persisted to `chroma_store/`
- **LLM:** `llama-3.3-70b-versatile` via Groq API
- **Framework:** LangChain (LCEL) · **UI:** Streamlit

---

## Requirements

- Python 3.11+
- A free [Groq API key](https://console.groq.com)

---

## Local setup

```bash
# 1. Clone the repo
git clone https://github.com/abidfayaz/novacell-telecom-chatbot.git
cd novacell-telecom-chatbot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Groq API key
cp .env.example .env
# Edit .env and paste your key: GROQ_API_KEY=gsk_...
```

The vector store is pre-built and committed to the repo — no ingestion step needed on first run.

## Run locally

```bash
streamlit run app.py
```

The first query downloads the ~90 MB embedding model into `~/.cache/huggingface/`. Subsequent queries use the cached model.

---

## Streamlit Cloud deployment

1. Fork or clone this repo to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect the repo
3. Set the main file path to `app.py`
4. In **App settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Deploy

The app reads `GROQ_API_KEY` from Streamlit Secrets on the cloud and from `.env` locally.

---

## Project layout

| File | Role |
|---|---|
| `config.py` | Paths, model names, retrieval depth, collection registry |
| `vectorstore.py` | Shared embeddings + ChromaDB helpers |
| `ingest_*.py` | One ingest script per knowledge source |
| `ingest_all.py` | Runs all ingest scripts in one pass |
| `retriever.py` | Parallel fan-out across collections, source labelling |
| `chain.py` | LCEL RAG chain (prompt + Groq LLM + parser) |
| `app.py` | Streamlit chat UI |
| `main.py` | CLI REPL (local testing) |
| `Data/` | Source knowledge files (CSV, SQLite, PDF, JSON) |
| `chroma_store/` | Pre-built vector store (committed; no re-ingestion needed) |

## Knowledge sources

| Collection | Source file | Documents |
|---|---|---|
| `faq` | `Data/faq.csv` | Question/answer pairs |
| `tickets` | `Data/tickets.db` | Resolved support tickets |
| `guides` | `Data/telecom_guide.pdf` | Chunked PDF (600 chars, 100 overlap) |
| `plans` | `Data/plans.json` | Mobile plans and add-ons |

To rebuild the vector store after editing a knowledge source: `python ingest_all.py`

---

## Known limitations

- Demo knowledge only — no real customer data
- No memory between sessions (each conversation starts fresh)
- Embedding model downloads ~90 MB on first query in a new environment
- Not production-hardened (no rate limiting, no auth)

---

## Extending

To add a new knowledge source: write a new `ingest_<source>.py` that builds a
Chroma collection, then register the collection name in `RETRIEVAL_COLLECTIONS`
in `config.py`. The retriever picks it up automatically without changes to
`retriever.py`, `chain.py`, or the UI.
