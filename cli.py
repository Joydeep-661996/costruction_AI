from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import json

from dpr_scheduler.ingest import read_wbs, read_dpr
from dpr_scheduler.dpr import apply_dpr_updates
from dpr_scheduler.cpm import recompute_with_progress
from dpr_scheduler.reporting import schedule_to_rows, lookahead, gantt_html


def write_templates(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "wbs_template.csv").write_text(
        """task_id,name,duration_days,dependencies,resource
T1,Site clearance,5,,Civil
T2,Excavation,10,T1,Civil
T3,Footings,7,T2,Civil
T4,Columns,10,T3,Structural
T5,Slab,8,T4,Structural
T6,MEP rough-in,12,T4;T5,MEP
T7,Finishes,15,T6,Finishes
"""
    )
    (out_dir / "dpr_template.csv").write_text(
        """date,task_id,percent_complete
2025-01-05,T1,100
2025-01-08,T2,30
2025-01-10,T2,50
2025-01-15,T3,20
"""
    )
    print(f"Templates written to {out_dir}")


def parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def cmd_schedule(args: argparse.Namespace) -> None:
    wbs_path = Path(args.wbs)
    dpr_path = Path(args.dpr)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = read_wbs(str(wbs_path))
    dpr = read_dpr(str(dpr_path))

    if args.project_start:
        project_start = parse_date(args.project_start)
    else:
        project_start = min((r.date for r in dpr), default=date.today())

    apply_dpr_updates(tasks, dpr)
    schedule = recompute_with_progress(tasks, project_start)

    rows = schedule_to_rows(schedule)

    # Save schedule as JSON and CSV (CSV simple writer)
    (out_dir / "schedule.json").write_text(json.dumps(rows, default=str, indent=2))
    with open(out_dir / "schedule.csv", "w", encoding="utf-8") as f:
        headers = list(rows[0].keys()) if rows else []
        if headers:
            f.write(",".join(headers) + "\n")
            for r in rows:
                values = [str(r.get(h, "")) for h in headers]
                f.write(",".join(values) + "\n")

    # Lookaheads
    la7 = lookahead(rows, start_date=date.today(), horizon_days=7)
    la14 = lookahead(rows, start_date=date.today(), horizon_days=14)
    la28 = lookahead(rows, start_date=date.today(), horizon_days=28)
    (out_dir / "lookahead_7d.json").write_text(json.dumps(la7, default=str, indent=2))
    (out_dir / "lookahead_14d.json").write_text(json.dumps(la14, default=str, indent=2))
    (out_dir / "lookahead_28d.json").write_text(json.dumps(la28, default=str, indent=2))

    # Gantt
    html = gantt_html(rows)
    (out_dir / "gantt.html").write_text(html)

    critical_path = ", ".join(schedule.critical_path)
    print("Schedule updated.")
    print(f"Critical Path: {critical_path}")
    print(f"Outputs written to {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="DPR-based Construction Scheduler")
    sub = parser.add_subparsers(dest="command", required=True)

    p_templates = sub.add_parser("templates", help="Write CSV templates")
    p_templates.add_argument("--out", required=True, help="Output directory for templates")

    p_schedule = sub.add_parser("schedule", help="Compute updated schedule from WBS and DPR")
    p_schedule.add_argument("--wbs", required=True, help="Path to WBS CSV/Excel")
    p_schedule.add_argument("--dpr", required=True, help="Path to DPR CSV/Excel")
    p_schedule.add_argument("--project-start", help="Project start date (YYYY-MM-DD)")
    p_schedule.add_argument("--out", required=True, help="Output directory for results")

    args = parser.parse_args()

    if args.command == "templates":
        write_templates(Path(args.out))
    elif args.command == "schedule":
        cmd_schedule(args)


if __name__ == "__main__":
    main()