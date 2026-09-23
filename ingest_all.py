"""Run every knowledge ingest in one pass.

Convenience entry point so a fresh checkout can build the whole vector store
with a single command:  ``python ingest_all.py``
"""

from __future__ import annotations

import ingest_faq
import ingest_guides
import ingest_plans
import ingest_tickets


def main() -> None:
    print("Building vector store from all knowledge sources...\n")
    total = 0
    total += ingest_faq.ingest()
    total += ingest_tickets.ingest()
    total += ingest_guides.ingest()
    total += ingest_plans.ingest()
    print(f"\nDone. {total} documents indexed across all collections.")


if __name__ == "__main__":
    main()
