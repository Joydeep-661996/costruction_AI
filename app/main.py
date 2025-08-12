from __future__ import annotations

from datetime import date, datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path

from dpr_scheduler.ingest import read_wbs, read_dpr
from dpr_scheduler.dpr import apply_dpr_updates
from dpr_scheduler.cpm import recompute_with_progress
from dpr_scheduler.reporting import schedule_to_rows, gantt_html

app = FastAPI(title="DPR-based Construction Scheduler")


def _save_upload_to_temp(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix or ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(upload.file.read())
    tmp.flush()
    tmp.close()
    return tmp.name


@app.post("/schedule")
async def schedule_endpoint(
    wbs: UploadFile = File(...),
    dpr: UploadFile = File(...),
    project_start: str | None = Form(None),
):
    try:
        wbs_path = _save_upload_to_temp(wbs)
        dpr_path = _save_upload_to_temp(dpr)

        tasks = read_wbs(wbs_path)
        dpr_records = read_dpr(dpr_path)

        if project_start:
            start_date = datetime.fromisoformat(project_start).date()
        else:
            start_date = min((r.date for r in dpr_records), default=date.today())

        apply_dpr_updates(tasks, dpr_records)
        schedule = recompute_with_progress(tasks, start_date)

        rows = schedule_to_rows(schedule)
        gantt = gantt_html(rows)

        return JSONResponse(
            content={
                "project_start": str(start_date),
                "critical_path": schedule.critical_path,
                "schedule": rows,
                "gantt_html": gantt,
            }
        )
    except Exception as ex:
        return JSONResponse(status_code=400, content={"error": str(ex)})