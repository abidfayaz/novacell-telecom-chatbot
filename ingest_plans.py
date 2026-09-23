"""Ingest mobile plans & add-ons into the `plans` Chroma collection.

One plan/add-on object from Data/plans.json -> one vector document. Each plan
is rendered into a readable, self-contained description so retrieval matches on
plan name, price, data, network, eligibility, or features.

Re-runs are idempotent (FR-17): the collection is reset and rebuilt from the
current JSON each time, so support ops can edit plans.json and re-run.
"""

from __future__ import annotations

import json

from langchain_core.documents import Document

from config import COLLECTION_PLANS, PLANS_JSON
from vectorstore import get_vectorstore, reset_collection


def _format_data(plan: dict) -> str:
    if plan.get("data_unlimited"):
        return "unlimited data"
    gb = plan.get("data_gb")
    if gb is None:
        return ""
    if isinstance(gb, (int, float)):
        return f"{gb} GB data"
    return str(gb)


def _format_plan(plan: dict, currency: str, operator: str) -> str:
    """Render a single plan/add-on into a human-readable paragraph."""
    parts: list[str] = []

    name = plan.get("name", plan.get("id", "Unknown plan"))
    ptype = plan.get("type", "")
    header = f"{operator} {name}"
    if ptype:
        header += f" ({ptype})"
    parts.append(header)

    # Pricing — plans use monthly_price; add-ons use price + price_unit.
    if plan.get("monthly_price") is not None:
        line = f"Price: {currency} {plan['monthly_price']}/month"
        if plan.get("price_per_line") is not None:
            line += f" ({currency} {plan['price_per_line']} per line)"
        if plan.get("lines_included") is not None:
            line += f", includes {plan['lines_included']} lines"
        parts.append(line)
    elif plan.get("price") is not None:
        unit = plan.get("price_unit", "")
        parts.append(f"Price: {currency} {plan['price']} {unit}".strip())

    data = _format_data(plan)
    if data:
        parts.append(f"Data: {data}")

    if plan.get("talk_minutes") is not None:
        parts.append(f"Talk: {plan['talk_minutes']}")
    if plan.get("texts") is not None:
        parts.append(f"Texts: {plan['texts']}")
    if plan.get("hotspot_gb"):
        parts.append(f"Hotspot: {plan['hotspot_gb']} GB")
    if plan.get("network"):
        parts.append(f"Network: {plan['network']}")
    if plan.get("coverage"):
        parts.append(f"Coverage: {plan['coverage']}")
    if plan.get("contract"):
        parts.append(f"Contract: {plan['contract']}")
    if plan.get("eligibility"):
        parts.append(f"Eligibility: {plan['eligibility']}")
    if plan.get("intro_offer"):
        parts.append(f"Intro offer: {plan['intro_offer']}")

    features = plan.get("features") or []
    if features:
        parts.append("Features: " + "; ".join(features))

    if plan.get("best_for"):
        parts.append(f"Best for: {plan['best_for']}")

    return "\n".join(parts)


def load_plan_documents() -> list[Document]:
    with open(PLANS_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)

    currency = payload.get("currency", "USD")
    operator = payload.get("operator", "")
    plans = payload.get("plans", [])

    docs: list[Document] = []
    for plan in plans:
        content = _format_plan(plan, currency, operator)
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": "plans",
                    "id": plan.get("id", ""),
                    "name": plan.get("name", ""),
                    "category": plan.get("category", ""),
                    "type": plan.get("type", ""),
                },
            )
        )
    return docs


def ingest() -> int:
    docs = load_plan_documents()
    if not docs:
        print("No plans found — nothing to ingest.")
        return 0

    reset_collection(COLLECTION_PLANS)
    store = get_vectorstore(COLLECTION_PLANS)
    ids = [f"plan-{doc.metadata.get('id') or i}" for i, doc in enumerate(docs)]
    store.add_documents(docs, ids=ids)
    print(f"Ingested {len(docs)} plans/add-ons into '{COLLECTION_PLANS}'.")
    return len(docs)


if __name__ == "__main__":
    ingest()
