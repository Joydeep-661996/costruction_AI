from __future__ import annotations

from datetime import date, timedelta
from typing import List, Dict, Any
import plotly.graph_objects as go

from .models import ProjectSchedule


def schedule_to_rows(schedule: ProjectSchedule) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for t in schedule.tasks:
        rows.append(
            {
                "task_id": t.task_id,
                "name": t.name,
                "resource": t.resource,
                "duration_days": t.duration_days,
                "percent_complete": round(t.percent_complete, 2) if t.percent_complete is not None else None,
                "early_start": t.early_start,
                "early_finish": t.early_finish,
                "late_start": t.late_start,
                "late_finish": t.late_finish,
                "total_float_days": t.total_float_days,
                "forecast_start": t.forecast_start,
                "forecast_finish": t.forecast_finish,
                "is_critical": t.total_float_days == 0 if t.total_float_days is not None else None,
            }
        )
    rows.sort(key=lambda r: (r.get("forecast_start") or r.get("early_start"), r.get("task_id")))
    return rows


def lookahead(rows: List[Dict[str, Any]], start_date: date, horizon_days: int) -> List[Dict[str, Any]]:
    end_date = start_date + timedelta(days=horizon_days)
    def intersects(r):
        s = r.get("forecast_start") or r.get("early_start")
        f = r.get("forecast_finish") or r.get("early_finish")
        if s is None or f is None:
            return False
        return (s < end_date) and (f >= start_date)

    selected = [
        {
            "task_id": r["task_id"],
            "name": r["name"],
            "resource": r.get("resource"),
            "percent_complete": r.get("percent_complete"),
            "forecast_start": r.get("forecast_start") or r.get("early_start"),
            "forecast_finish": r.get("forecast_finish") or r.get("early_finish"),
            "is_critical": r.get("is_critical"),
        }
        for r in rows
        if intersects(r)
    ]
    selected.sort(key=lambda r: (r.get("forecast_start"), not bool(r.get("is_critical")), r.get("task_id")))
    return selected


def gantt_html(rows: List[Dict[str, Any]], title: str = "Updated Schedule Gantt") -> str:
    names = []
    starts = []
    finishes = []
    colors = []
    hovertexts = []

    for r in rows:
        start = r.get("forecast_start") or r.get("early_start")
        finish = r.get("forecast_finish") or r.get("early_finish")
        if start is None or finish is None:
            continue
        names.append(r["name"])  # y-axis labels
        starts.append(start)
        finishes.append(finish)
        is_critical = r.get("is_critical")
        colors.append("#d62728" if is_critical else "#1f77b4")
        hovertexts.append(
            f"Task: {r['task_id']}<br>Resource: {r.get('resource') or ''}<br>"
            f"Progress: {r.get('percent_complete') or 0}%<br>Float: {r.get('total_float_days') or ''}d"
        )

    fig = go.Figure()
    for y, s, f, c, h in zip(names, starts, finishes, colors, hovertexts):
        fig.add_trace(
            go.Bar(
                x=[(f - s).days],
                y=[y],
                base=[s],
                orientation="h",
                marker_color=c,
                hovertext=h,
                hoverinfo="text",
            )
        )

    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis_title="Date",
        yaxis_title="Task",
        showlegend=False,
    )
    fig.update_yaxes(autorange="reversed")
    return fig.to_html(include_plotlyjs="cdn", full_html=True)