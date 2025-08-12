from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Tuple
import networkx as nx

from .models import Task, ProjectSchedule


def _add_days(start: date, days: int) -> date:
    return start + timedelta(days=days)


def build_dag(tasks: List[Task]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for task in tasks:
        graph.add_node(task.task_id, task=task)
    for task in tasks:
        for dep in task.dependencies:
            if dep not in graph:
                raise ValueError(f"Dependency '{dep}' not found for task '{task.task_id}'")
            graph.add_edge(dep, task.task_id)
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Dependency graph must be a DAG (no cycles).")
    return graph


def forward_pass(graph: nx.DiGraph, project_start: date) -> None:
    topological = list(nx.topological_sort(graph))

    for node in topological:
        task: Task = graph.nodes[node]["task"]
        if graph.in_degree(node) == 0:
            es = project_start
        else:
            pred_efs = [graph.nodes[pred]["task"].early_finish for pred in graph.predecessors(node)]
            es = max(pred_efs)
        ef = _add_days(es, task.duration_days)
        task.early_start = es
        task.early_finish = ef


def backward_pass(graph: nx.DiGraph, project_finish: date) -> None:
    reverse_topo = list(reversed(list(nx.topological_sort(graph))))

    for node in reverse_topo:
        task: Task = graph.nodes[node]["task"]
        if graph.out_degree(node) == 0:
            lf = project_finish
        else:
            succ_lss = [graph.nodes[succ]["task"].late_start for succ in graph.successors(node)]
            lf = min(succ_lss)
        ls = lf - (task.early_finish - task.early_start)
        task.late_start = ls
        task.late_finish = lf
        task.total_float_days = (task.late_start - task.early_start).days


def compute_cpm(tasks: List[Task], project_start: date) -> Tuple[ProjectSchedule, nx.DiGraph]:
    graph = build_dag(tasks)
    forward_pass(graph, project_start)
    project_finish = max(graph.nodes[n]["task"].early_finish for n in graph.nodes)
    backward_pass(graph, project_finish)

    critical_nodes = [n for n in nx.topological_sort(graph) if graph.nodes[n]["task"].total_float_days == 0]

    schedule = ProjectSchedule(project_start=project_start, tasks=[graph.nodes[n]["task"] for n in graph.nodes])
    schedule.critical_path = critical_nodes
    return schedule, graph


def apply_forecast_from_progress(graph: nx.DiGraph, project_start: date) -> None:
    for node in nx.topological_sort(graph):
        task: Task = graph.nodes[node]["task"]
        if graph.in_degree(node) == 0:
            earliest_forecast_start = project_start
        else:
            earliest_forecast_start = max(
                graph.nodes[pred]["task"].forecast_finish for pred in graph.predecessors(node)
            )

        remaining = max(0, int(round(task.duration_days * (1.0 - task.percent_complete / 100.0))))
        if task.duration_days > 0 and 0 < task.percent_complete < 100.0 and remaining == 0:
            remaining = 1

        task.forecast_start = earliest_forecast_start
        task.forecast_finish = _add_days(earliest_forecast_start, remaining)


def recompute_with_progress(tasks: List[Task], project_start: date) -> ProjectSchedule:
    schedule, graph = compute_cpm(tasks, project_start)
    apply_forecast_from_progress(graph, project_start)

    cloned_tasks: List[Task] = []
    for t in tasks:
        remaining = max(0, int(round(t.duration_days * (1.0 - t.percent_complete / 100.0))))
        if t.duration_days > 0 and 0 < t.percent_complete < 100.0 and remaining == 0:
            remaining = 1
        cloned_tasks.append(
            Task(
                task_id=t.task_id,
                name=t.name,
                duration_days=remaining,
                dependencies=list(t.dependencies),
                resource=t.resource,
                percent_complete=t.percent_complete,
            )
        )

    forecast_schedule, _ = compute_cpm(cloned_tasks, project_start)
    schedule.critical_path = forecast_schedule.critical_path

    id_to_forecast = {t.task_id: t for t in forecast_schedule.tasks}
    for t in schedule.tasks:
        f = id_to_forecast[t.task_id]
        t.total_float_days = f.total_float_days

    return schedule