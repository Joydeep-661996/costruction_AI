from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import yaml


@dataclass
class Task:
    task_id: str
    name: str
    duration_days: int
    dependencies: List[str] = field(default_factory=list)
    planned_start: datetime | None = None
    planned_end: datetime | None = None

    def set_schedule(self, start_date: datetime):
        self.planned_start = start_date
        self.planned_end = start_date + timedelta(days=self.duration_days)


class Schedule:
    def __init__(self, tasks: Dict[str, Task]):
        self.tasks = tasks  # dict by task_id

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "Schedule":
        yaml_path = Path(yaml_path)
        data = yaml.safe_load(yaml_path.read_text())
        tasks_dict: Dict[str, Task] = {}
        for item in data:
            task = Task(
                task_id=item["task_id"],
                name=item["name"],
                duration_days=item["duration_days"],
                dependencies=item.get("dependencies", []),
            )
            tasks_dict[task.task_id] = task
        sched = cls(tasks_dict)
        sched._compute_baseline()
        return sched

    def _compute_baseline(self):
        """Compute baseline schedule using simple forward pass (ASAP)."""
        start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        calculated: Dict[str, datetime] = {}

        def calculate_task(task_id: str):
            if task_id in calculated:
                return calculated[task_id]
            task = self.tasks[task_id]
            if not task.dependencies:
                task.set_schedule(start_date)
            else:
                dep_end_dates = [calculate_task(dep) for dep in task.dependencies]
                task.set_schedule(max(dep_end_dates))
            calculated[task_id] = task.planned_end
            return task.planned_end

        for tid in self.tasks:
            calculate_task(tid)

    def to_dataframe(self):
        import pandas as pd

        rows = []
        for task in self.tasks.values():
            rows.append(
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "duration_days": task.duration_days,
                    "dependencies": ",".join(task.dependencies),
                    "start": task.planned_start,
                    "end": task.planned_end,
                }
            )
        return pd.DataFrame(rows)