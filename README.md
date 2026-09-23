# NovaCell Telecom Care Bot

A portfolio prototype exploring one product question:

> **What should an AI support assistant do when company knowledge is incomplete?**

NovaCell is a hypothetical mobile operator with ~4 million subscribers. Most support contacts are Tier-1, self-resolvable questions whose answers already exist across company knowledge sources. **MyTelecom** is the customer-facing app used in the prototype.

**Live demo:** [novacell-telecom-chatbot.streamlit.app](https://novacell-telecom-chatbot.streamlit.app/)

> **Portfolio demo.** Uses approved sample telecom knowledge. No access to live customer accounts, billing or usage data.

---

## My role

I owned the **product problem, scope, requirements, product rules, evaluation criteria and iteration decisions**.

AI coding tools were used to accelerate implementation. The product choices documented here — including grounded answers, safe refusal, escalation boundaries and extensibility — were deliberate PM decisions that I defined and tested.

---

## The problem

NovaCell's support knowledge is spread across:
- FAQs
- past resolved tickets
- official user guides
- mobile-plan information

Customers may wait for support even when the answer already exists somewhere in those sources.

The product hypothesis was:

> **A useful support assistant does not need to answer everything. It needs to answer supported questions reliably and fail safely when support knowledge is insufficient.**

---

## Key product decisions

### 1. Company knowledge over model memory
The assistant answers only from retrieved NovaCell knowledge. It does not use general model knowledge to fill gaps.

### 2. Safe refusal is part of the product
If the retrieved knowledge is insufficient, the assistant says so and routes the user to the **MyTelecom app or 611** instead of guessing.

### 3. Personal account data is a hard boundary
The prototype has no live billing, usage or customer-account access. It never implies otherwise.

### 4. The knowledge layer should expand without rebuilding the product
The initial system used three sources. I later added a fourth source containing **14 plans and add-ons**.

That required:
- one new ingestion path
- one configuration change
- no changes to retrieval, generation or UI logic

This was used as a practical test of extensibility rather than treating modularity as a design claim.

---

## Validation so far

Validation is manual and scenario-based.

- Supported telecom questions were answered from the approved knowledge sources.
- An unsupported question was refused instead of answered from general model knowledge.
- Adding the fourth knowledge source enabled plan-related questions without changing the downstream experience.

This is **prototype-level validation**, not production-scale evaluation or customer-adoption evidence.

---

## What the demo does

- Answers Tier-1 questions about connectivity, data, roaming, SIM/eSIM, billing and plans
- Retrieves from four knowledge sources before generating a response
- Refuses unsupported questions rather than improvising
- Provides a simple Streamlit interface with sample questions
- Preserves no user account data and has no live telecom-system integration

---

## Current architecture

```
User question
     |
     v
Parallel retrieval across four ChromaDB collections
  - FAQ
  - Resolved tickets
  - User guides
  - Mobile plans
     |
     v
Source-labelled context
     |
     v
Grounded prompt with refusal rules
     |
     v
Groq-hosted LLM
     |
     v
Streamed response in Streamlit
```

**Current implementation**
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Vector store: ChromaDB
- LLM: `openai/gpt-oss-20b` via Groq
- Orchestration: LangChain LCEL
- UI: Streamlit
- Retrieval: top 3 results from each of 4 sources

---

## Knowledge sources

| Collection | Source | Purpose |
|---|---|---|
| FAQ | `Data/faq.csv` | Common questions and approved answers |
| Resolved tickets | `Data/tickets.db` | Past support issues and resolutions |
| User guides | `Data/telecom_guide.pdf` | Step-by-step troubleshooting guidance |
| Mobile plans | `Data/plans.json` | 14 plans and add-ons |

---

## Known limitations

- Manual evaluation only
- No automated regression suite
- No real customer traffic
- No production monitoring
- No live CRM, billing or usage integration
- No session-aware retrieval across turns
- Not production-hardened

The next product priority would be **repeatable evaluation**, not additional features.

---

## Run locally

### Requirements
- Python 3.11+
- A Groq API key

### Setup

```bash
git clone https://github.com/abidfayaz/novacell-telecom-chatbot.git
cd novacell-telecom-chatbot
pip install -r requirements.txt
cp .env.example .env
# Add your Groq key to .env
```

The vector store is pre-built and committed to the repository.

### Start the app

```bash
streamlit run app.py
```

For Streamlit Cloud, add `GROQ_API_KEY` under **App settings → Secrets**.

---

## Repository structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface |
| `chain.py` | Grounded generation and refusal rules |
| `retriever.py` | Parallel retrieval across knowledge sources |
| `config.py` | Shared model, retrieval and path configuration |
| `ingest_*.py` | Knowledge-source ingestion |
| `Data/` | Sample knowledge files |
| `chroma_store/` | Pre-built vector store |
| `PRD.md` | Original product requirements exercise |
| `PROBLEM_STATEMENT.txt` | Original product brief |

---

## Product principle

> **The assistant should never sound more confident than the knowledge available to it.**

That principle shaped the grounding rules, escalation behaviour and evaluation focus of the prototype.
