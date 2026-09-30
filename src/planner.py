from typing import Dict, Any, List
from src.database import get_all_tasks, mark_task_status


def get_planner_summary() -> Dict[str, Any]:
    tasks = get_all_tasks()
    if not tasks:
        return {
            "has_roadmap": False,
            "total_tasks": 0,
            "completed_tasks": 0,
            "progress_percent": 0.0,
            "current_phase": "N/A",
            "active_task": None,
            "has_incomplete_previous": False,
            "all_completed": False,
            "all_tasks": []
        }

    total = len(tasks)
    completed_tasks = [t for t in tasks if t["completed"] == 1]
    completed_count = len(completed_tasks)
    progress_percent = round((completed_count / total) * 100, 1) if total > 0 else 0.0

    incomplete_tasks = [t for t in tasks if t["completed"] == 0]

    if not incomplete_tasks:
        return {
            "has_roadmap": True,
            "total_tasks": total,
            "completed_tasks": completed_count,
            "progress_percent": 100.0,
            "current_phase": tasks[-1]["phase_title"],
            "active_task": None,
            "has_incomplete_previous": False,
            "all_completed": True,
            "all_tasks": tasks
        }

    active_task = incomplete_tasks[0]
    first_incomplete_day = active_task["day_number"]
    
    current_day = len(completed_tasks) + 1
    has_incomplete_previous = first_incomplete_day < current_day or len(incomplete_tasks) > 1

    return {
        "has_roadmap": True,
        "total_tasks": total,
        "completed_tasks": completed_count,
        "progress_percent": progress_percent,
        "current_phase": active_task["phase_title"],
        "active_task": active_task,
        "has_incomplete_previous": has_incomplete_previous,
        "all_completed": False,
        "all_tasks": tasks
    }


def update_task_completion(task_id: int, completed: bool) -> None:
    mark_task_status(task_id, completed)
