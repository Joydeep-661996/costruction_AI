# DPR-based Construction Scheduler

A small program to generate updated construction schedules, Gantt charts, and short-term lookahead plans based on on-site Daily Progress Report (DPR) updates.

## Features
- Read WBS (tasks with durations and dependencies) from CSV/Excel
- Read DPR (cumulative task progress by date) from CSV/Excel
- Calculate CPM schedule, identify critical path, float
- Update forecast dates based on latest DPR progress
- Export schedule CSV, 7/14/28-day lookahead CSVs, and a Gantt chart HTML
- CLI and FastAPI API

## Install
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Inputs
- WBS file (CSV/Excel) with columns:
  - task_id (string)
  - name (string)
  - duration_days (int)
  - dependencies (comma-separated task_ids; optional)
  - resource (optional)
- DPR file (CSV/Excel) with columns:
  - date (YYYY-MM-DD)
  - task_id (string)
  - percent_complete (0-100, cumulative)

## CLI Usage
```bash
# Generate templates
python cli.py templates --out ./examples

# Compute updated schedule
python cli.py schedule \
  --wbs ./examples/wbs_template.csv \
  --dpr ./examples/dpr_template.csv \
  --project-start 2025-01-01 \
  --out ./outputs
```

Outputs in `--out`:
- schedule.csv
- lookahead_7d.csv, lookahead_14d.csv, lookahead_28d.csv
- gantt.html

## API Usage
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

POST `/schedule` (multipart/form-data):
- wbs: file
- dpr: file
- project_start: optional ISO date (YYYY-MM-DD)

Response: JSON with updated schedule, critical path, and Gantt HTML (inline string).

## Notes
- Dates assume calendar days (no working-day calendar). You can extend `calendar` logic in code if needed.
- For quantities/productivity-based progress, adapt `dpr_scheduler/dpr.py` to convert quantities to percent.