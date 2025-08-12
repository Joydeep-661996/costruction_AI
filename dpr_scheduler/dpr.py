from __future__ import annotations

from typing import Dict, List
from collections import defaultdict
from .models import Task, DPRRecord


def apply_dpr_updates(tasks: List[Task], dpr_records: List[DPRRecord]) -> None:
    """
    Mutates tasks to reflect the latest cumulative percent_complete per task from DPR.
    If multiple records exist for a task, the latest by date is used.
    """
    latest_by_task: Dict[str, DPRRecord] = {}
    for record in dpr_records:
        prev = latest_by_task.get(record.task_id)
        if prev is None or record.date > prev.date:
            latest_by_task[record.task_id] = record

    for task in tasks:
        if task.task_id in latest_by_task:
            task.percent_complete = latest_by_task[task.task_id].percent_complete
            if task.percent_complete > 100.0:
                task.percent_complete = 100.0
            if task.percent_complete < 0.0:
                task.percent_complete = 0.0