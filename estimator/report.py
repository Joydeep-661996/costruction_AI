from __future__ import annotations

from pathlib import Path
from typing import List, Optional

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pd = None  # type: ignore

from .calculator import EstimatedItem


def as_dataframe(items: List[EstimatedItem]):
    if pd is None:
        return None
    rows = [
        {
            "Item": it.item_id,
            "Description": it.description,
            "Unit": it.unit,
            "Quantity": it.quantity,
            "Unit Rate": it.unit_rate,
            "Amount": it.amount,
            "Activity": it.activity,
            "Matched Keyword": it.matched_keyword,
        }
        for it in items
    ]
    return pd.DataFrame(rows)


def save_csv(items: List[EstimatedItem], path: Path) -> None:
    if pd is not None:
        df = as_dataframe(items)
        if df is not None:
            df.to_csv(path, index=False)
            return
    # Fallback simple CSV write
    with path.open("w", encoding="utf-8") as f:
        headers = [
            "Item",
            "Description",
            "Unit",
            "Quantity",
            "Unit Rate",
            "Amount",
            "Activity",
            "Matched Keyword",
        ]
        f.write(",".join(headers) + "\n")
        for it in items:
            row = [
                str(it.item_id or ""),
                '"' + (it.description or "").replace('"', '""') + '"',
                str(it.unit or ""),
                str(it.quantity),
                str(it.unit_rate if it.unit_rate is not None else ""),
                str(it.amount if it.amount is not None else ""),
                str(it.activity or ""),
                str(it.matched_keyword or ""),
            ]
            f.write(",".join(row) + "\n")


def save_excel(items: List[EstimatedItem], path: Path) -> Optional[Path]:
    if pd is None:
        return None
    df = as_dataframe(items)
    if df is None:
        return None
    try:
        df.to_excel(path, index=False)
        return path
    except Exception:
        return None


def save_summary_html(total: float, by_activity: dict, path: Path) -> None:
    html = [
        "<html><head><meta charset='utf-8'><title>Estimate Summary</title>",
        "<style>body{font-family:Arial, sans-serif;padding:24px;}table{border-collapse:collapse;}th,td{border:1px solid #ddd;padding:8px;}th{background:#f6f6f6;}</style>",
        "</head><body>",
        "<h2>Total Estimate</h2>",
        f"<p><strong>Total:</strong> {total:,.2f}</p>",
        "<h3>By Activity</h3>",
        "<table><thead><tr><th>Activity</th><th>Amount</th></tr></thead><tbody>",
    ]
    for activity, amount in sorted(by_activity.items(), key=lambda kv: kv[0].lower()):
        html.append(f"<tr><td>{activity}</td><td style='text-align:right'>{amount:,.2f}</td></tr>")
    html.extend(["</tbody></table>", "</body></html>"])
    path.write_text("".join(html), encoding="utf-8")