"""The RAG chain: retrieve -> prompt -> Llama 3.3 70B on Groq -> parsed text.

Implements the LCEL pipeline from the architecture diagram. The LLM is
instructed to answer using ONLY the retrieved context (FR-10) and to escalate
to 611 / MyTelecom when the context is insufficient (FR-11). Temperature is 0
for deterministic output (FR-12).
"""

from __future__ import annotations

import functools
from typing import Iterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_groq import ChatGroq

from config import (
    ESCALATION_MESSAGE,
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
)
from retriever import retrieve_context

SYSTEM_PROMPT = """You are MyTelecom's customer-care assistant. You help \
subscribers resolve common Tier-1 support issues (connectivity, data, \
roaming, SIM/eSIM, billing, voice, device, and account questions) and answer \
questions about available mobile plans, add-ons, and pricing.

Strict rules:
1. Answer using ONLY the information in the CONTEXT below. Do NOT use any \
outside or prior knowledge, and never invent prices, policies, steps, or facts.
2. If the context does not contain enough information to answer confidently, \
do not guess. Reply exactly with: "{escalation}"
3. You have no access to live account, billing, or usage data. If the user \
asks about their personal account specifics (e.g. their balance or their \
charges), explain that you can't see personal account data and direct them to \
the MyTelecom app or 611.
4. Be concise, friendly, and give clear step-by-step instructions when the \
context provides them.

CONTEXT:
{context}"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
).partial(escalation=ESCALATION_MESSAGE)


@functools.lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=GROQ_API_KEY,
    )


@functools.lru_cache(maxsize=1)
def build_chain():
    """Assemble the LCEL RAG chain."""
    return (
        {
            "context": RunnableLambda(retrieve_context),
            "question": RunnablePassthrough(),
        }
        | PROMPT
        | get_llm()
        | StrOutputParser()
    )


def answer(question: str) -> str:
    """Return a complete grounded answer for a question (non-streaming)."""
    return build_chain().invoke(question)


def stream_answer(question: str) -> Iterator[str]:
    """Yield the grounded answer token-by-token (FR-05)."""
    yield from build_chain().stream(question)
