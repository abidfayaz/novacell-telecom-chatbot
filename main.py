"""Interactive CLI REPL for the telecom chatbot (FR-18).

Usage:
    python main.py

Type a question and the grounded answer streams back. Type 'quit' to exit
(FR-19).
"""

from __future__ import annotations

import sys

from chain import stream_answer


def main() -> None:
    print("=" * 60)
    print("  MyTelecom Customer Care Assistant (CLI)")
    print("  Ask a question, or type 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        print("\nAssistant: ", end="", flush=True)
        try:
            for token in stream_answer(question):
                print(token, end="", flush=True)
            print()
        except Exception as exc:  # surface config/network errors clearly
            print(f"\n[error] {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
