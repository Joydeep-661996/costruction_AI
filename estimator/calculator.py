from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .parsing import BoQItem
from .rate_db import RateDatabase, RateRule


@dataclass
class EstimatedItem:
    item_id: Optional[str]
    description: str
    unit: Optional[str]
    quantity: float
    unit_rate: Optional[float]
    amount: Optional[float]
    activity: Optional[str]
    matched_keyword: Optional[str]


def estimate_items(boq_items: List[BoQItem], rate_db: RateDatabase) -> List[EstimatedItem]:
    results: List[EstimatedItem] = []
    for it in boq_items:
        qty = it.quantity or 0.0
        match: Optional[RateRule] = rate_db.find_best_match(it.description, it.unit)
        unit_rate = match.unit_rate if match else None
        amount = (qty * unit_rate) if (unit_rate is not None) else None
        activity = (match.activity if match and match.activity else it.activity)
        results.append(
            EstimatedItem(
                item_id=it.item_id,
                description=it.description,
                unit=it.unit,
                quantity=qty,
                unit_rate=unit_rate,
                amount=amount,
                activity=activity,
                matched_keyword=(match.keyword if match else None),
            )
        )
    return results


def summarize_totals(items: List[EstimatedItem]) -> dict:
    total = sum((it.amount or 0.0) for it in items)
    by_activity: dict = {}
    for it in items:
        key = it.activity or "Uncategorized"
        by_activity[key] = by_activity.get(key, 0.0) + (it.amount or 0.0)
    return {"total": total, "by_activity": by_activity}