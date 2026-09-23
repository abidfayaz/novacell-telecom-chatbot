"""Streamlit chat UI for the telecom RAG chatbot.

Run with:
    streamlit run app.py

Features: free-text questions (FR-01), clickable sample questions (FR-02),
in-session history (FR-03), clear-conversation (FR-04), and streamed responses
(FR-05). No login / no setup (Goal: accessible to non-technical users).
"""

from __future__ import annotations

import os

import streamlit as st

# Inject Streamlit Secret as env var before any other module reads config.
# This makes the app work on Streamlit Cloud (secrets) and locally (.env) unchanged.
if not os.getenv("GROQ_API_KEY"):
    try:
        _key = st.secrets.get("GROQ_API_KEY", "")
        if _key:
            os.environ["GROQ_API_KEY"] = _key
    except Exception:
        pass

from chain import stream_answer  # noqa: E402 — must follow secret injection
from config import GROQ_API_KEY  # noqa: E402

SAMPLE_QUESTIONS = [
    "Why is my mobile internet so slow?",
    "How do I activate international roaming before a trip?",
    "Why is my bill higher than usual?",
    "My phone shows 'SIM not detected' — what should I do?",
    "How do I enable VoLTE?",
    "Can I keep my number when switching networks?",
]

DEMO_BANNER = (
    "**Portfolio demo** using approved sample telecom knowledge. "
    "No access to live customer accounts, billing or usage data."
)

GITHUB_URL = "https://github.com/abidfayaz/novacell-telecom-chatbot"

st.set_page_config(page_title="MyTelecom Care Assistant", page_icon="📶")


def ensure_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending" not in st.session_state:
        st.session_state.pending = None


def render_history() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def handle_question(question: str) -> None:
    """Append the user turn, stream the assistant reply, and store it."""
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            response = st.write_stream(stream_answer(question))  # FR-05
        except Exception:
            response = (
                "The AI service is temporarily unavailable. "
                "Please try again shortly."
            )
            st.warning(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


def main() -> None:
    ensure_state()

    st.info(DEMO_BANNER, icon="ℹ️")

    st.title("📶 MyTelecom Customer Care Assistant")
    st.caption(
        "Answers are grounded only in MyTelecom's FAQ, resolved tickets, user guides, "
        "and mobile plans. For personal account details, use the MyTelecom app or call 611."
    )

    with st.sidebar:
        st.header("Sample questions")
        for q in SAMPLE_QUESTIONS:
            if st.button(q, use_container_width=True):
                st.session_state.pending = q  # FR-02

        st.divider()
        if st.button("🗑️ Clear conversation", use_container_width=True):  # FR-04
            st.session_state.messages = []
            st.session_state.pending = None
            st.rerun()

        st.divider()
        st.markdown(
            f"[📂 View source on GitHub]({GITHUB_URL})",
            unsafe_allow_html=False,
        )

    if not GROQ_API_KEY:
        st.warning(
            "GROQ_API_KEY is not set. Add it to `.env` locally, or to Streamlit "
            "Secrets on Streamlit Cloud, then restart the app."
        )

    render_history()

    typed = st.chat_input("Ask about connectivity, billing, SIM, roaming...")
    question = typed or st.session_state.pending
    if question:
        st.session_state.pending = None
        handle_question(question)


if __name__ == "__main__":
    main()
