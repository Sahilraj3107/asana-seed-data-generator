import random
from ..utils.ids import gid
from ..utils.dates import random_past_datetime, iso_ts, iso_date, now_utc

def gen_tasks(workspace_id: str, projects, sections_by_project, users, n_tasks: int, history_days: int):
    out = []
    for _ in range(n_tasks):
        p = random.choice(projects)
        secs = sections_by_project[p["project_id"]]
        sec = random.choice(secs)
        created = random_past_datetime(history_days)
        updated = created if random.random() < 0.2 else random_past_datetime(history_days)
        if updated < created:
            updated = created

        completed = 1 if random.random() < 0.55 else 0
        completed_at = None
        if completed:
            # ensure after created
            completed_at = iso_ts(max(created, random_past_datetime(history_days)))

        due_on = None
        if random.random() < 0.75:
            # due date between -14 and +60 days around creation (some overdue)
            offset = random.randint(-14, 60)
            due_on = iso_date(created + __import__("datetime").timedelta(days=offset))

        assignee_id = None if random.random() < 0.15 else random.choice(users)["user_id"]

        out.append({
            "task_id": gid(),
            "workspace_id": workspace_id,
            "project_id": p["project_id"],
            "section_id": sec["section_id"],
            "parent_task_id": None,  # add subtasks in second pass
            "name": random.choice([
                "Fix flaky integration test",
                "Draft launch email copy",
                "Review Q2 OKR alignment",
                "Investigate latency regression",
                "Update onboarding checklist",
                "Prepare stakeholder demo"
            ]),
            "description": None,
            "created_by": p["created_by"],
            "assignee_id": assignee_id,
            "due_on": due_on,
            "start_on": None,
            "created_at": iso_ts(created),
            "updated_at": iso_ts(updated),
            "completed": completed,
            "completed_at": completed_at,
            "priority": random.choice([None, "P0", "P1", "P2", "P3"]),
        })
    return out

def add_subtasks(tasks, pct_subtasks: float = 0.25):
    by_project = {}
    for t in tasks:
        by_project.setdefault(t["project_id"], []).append(t)

    for project_id, ts in by_project.items():
        if len(ts) < 5:
            continue

        # Only top-level tasks can be parents
        top_level = [t for t in ts if t["parent_task_id"] is None]
        if len(top_level) < 2:
            continue

        n = int(len(ts) * pct_subtasks)
        candidates = random.sample(ts, n)

        for c in candidates:
            parent = random.choice(top_level)
            if c["task_id"] != parent["task_id"]:
                c["parent_task_id"] = parent["task_id"]
                c["section_id"] = parent["section_id"]
