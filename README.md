# Construction Scheduler

A simple program to generate construction schedules and Gantt charts based on task definitions and DPR (Daily Progress Report) updates.

## Features

* Define project activities, durations, and dependencies in a YAML file.
* Compute a baseline schedule using a forward-pass algorithm.
* (Optional) Load site DPR updates (CSV/JSON) for future integration.
* Export a Gantt chart as a PNG image.

## Requirements

```
pip install -r requirements.txt
```

## Usage

```
python -m construction_scheduler sample_tasks.yaml --dpr sample_dpr.csv --output-image my_schedule.png
```

* `sample_tasks.yaml` – Activity definitions.
* `--dpr` – Optional DPR file containing daily activity progress.
* `--output-image` – Destination filename for the Gantt chart.

The script prints the planned schedule in tabular form and saves a Gantt chart image.

## File Formats

### Tasks YAML

Each task entry requires:

```
- task_id: UNIQUE_ID
  name: Descriptive Name
  duration_days: <int>
  dependencies: [LIST, OF, TASK_IDS]
```

### DPR CSV/JSON

```
date,activity,progress
2025-08-12,EXCAVATION,80
```

* `date` – Date of update.
* `activity` – Task ID matching `task_id` in YAML.
* `progress` – Percent complete on that date.

## Roadmap

* Incorporate DPR progress to shift future start dates automatically.
* Add critical path and slack time calculations.
* Generate PDF reports.