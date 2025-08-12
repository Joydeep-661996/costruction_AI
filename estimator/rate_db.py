from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class RateRule:
    keyword: str
    unit: Optional[str]
    unit_rate: float
    activity: Optional[str] = None


class RateDatabase:
    def __init__(self, rules: List[RateRule]):
        self.rules = rules

    @classmethod
    def load_from_csv(cls, csv_path: Path) -> "RateDatabase":
        rules: List[RateRule] = []
        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"keyword", "unit", "unit_rate"}
            missing = required - set(h.strip().lower() for h in reader.fieldnames or [])
            if missing:
                raise ValueError(f"Rates CSV must include headers: {', '.join(sorted(required))}")
            for row in reader:
                keyword = (row.get("keyword") or "").strip()
                unit = (row.get("unit") or "").strip() or None
                rate_str = (row.get("unit_rate") or "").strip()
                activity = (row.get("activity") or "").strip() or None
                if not keyword or not rate_str:
                    continue
                try:
                    rate = float(rate_str)
                except Exception:
                    continue
                rules.append(RateRule(keyword=keyword, unit=unit, unit_rate=rate, activity=activity))
        return cls(rules)

    def find_best_match(self, description: str, unit: Optional[str]) -> Optional[RateRule]:
        desc = description.lower()
        unit_norm = (unit or "").lower()
        candidates: List[RateRule] = []
        for r in self.rules:
            if r.unit and unit_norm and r.unit.lower() != unit_norm:
                continue
            if r.keyword.lower() in desc:
                candidates.append(r)
        if not candidates and unit_norm:
            # Looser: allow unit-only default rules (keyword="*" or empty)
            for r in self.rules:
                if r.keyword.strip() in {"*", ""} and (r.unit or "").lower() == unit_norm:
                    candidates.append(r)
        if not candidates:
            return None
        # Choose the most specific keyword (longest keyword wins); tie-breaker: has activity
        candidates.sort(key=lambda r: (len(r.keyword), 1 if r.activity else 0), reverse=True)
        return candidates[0]