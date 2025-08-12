from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .boq_extractor import extract_boq
from .calculator import estimate_items, summarize_totals
from .rate_db import RateDatabase
from .report import save_csv, save_excel, save_summary_html


def run_cli(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Construction Project Estimator: extract BOQ from documents/drawings and compute totals.",
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Input files or directories containing tender documents and drawings (PDF, PNG, JPG, TIFF)",
    )
    parser.add_argument(
        "--rates",
        required=True,
        help="CSV file with unit rates. Headers: keyword,unit,unit_rate[,activity]",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write outputs (CSV, optional Excel, HTML summary)",
    )
    parser.add_argument(
        "--contingency-pct",
        type=float,
        default=0.0,
        help="Optional contingency percentage to add to total (e.g., 10 for 10%%)",
    )
    parser.add_argument(
        "--tax-pct",
        type=float,
        default=0.0,
        help="Optional tax percentage to add to total (e.g., 5 for 5%%)",
    )

    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rate_db = RateDatabase.load_from_csv(Path(args.rates))

    boq_items = extract_boq(args.inputs)

    estimated = estimate_items(boq_items, rate_db)

    csv_path = output_dir / "estimate.csv"
    save_csv(estimated, csv_path)

    # Try Excel if possible
    excel_path = output_dir / "estimate.xlsx"
    save_excel(estimated, excel_path)

    summary = summarize_totals(estimated)
    total = summary["total"]
    by_activity = summary["by_activity"]

    # Apply contingency and tax to total (not to per-activity breakdown)
    contingency = (args.contingency_pct / 100.0) * total
    subtotal = total + contingency
    tax = (args.tax_pct / 100.0) * subtotal
    grand_total = subtotal + tax

    html_path = output_dir / "summary.html"
    save_summary_html(grand_total, by_activity, html_path)

    print(f"Wrote: {csv_path}")
    if excel_path.exists():
        print(f"Wrote: {excel_path}")
    print(f"Wrote: {html_path}")
    print(f"Grand Total (incl. contingency {args.contingency_pct:.2f}% and tax {args.tax_pct:.2f}%): {grand_total:,.2f}")

    # Exit code 0 for success
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())