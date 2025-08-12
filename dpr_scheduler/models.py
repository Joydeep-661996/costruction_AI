from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict


@dataclass
class Task:
    task_id: str
    name: str
    duration_days: int
    dependencies: List[str] = field(default_factory=list)
    resource: Optional[str] = None

    # Progress attributes (updated from DPR)
    percent_complete: float = 0.0

    # Computed scheduling fields (CPM)
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    late_start: Optional[date] = None
    late_finish: Optional[date] = None
    total_float_days: Optional[int] = None

    # Forecast fields (after DPR)
    forecast_start: Optional[date] = None
    forecast_finish: Optional[date] = None


@dataclass
class DPRRecord:
    date: date
    task_id: str
    percent_complete: float


@dataclass
class ProjectSchedule:
    project_start: date
    tasks: List[Task]
    critical_path: List[str] = field(default_factory=list)

    def task_by_id(self) -> Dict[str, Task]:
        return {t.task_id: t for t in self.tasks}