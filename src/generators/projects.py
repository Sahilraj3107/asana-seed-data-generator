import random
from ..utils.ids import gid
from ..utils.dates import random_past_datetime, iso_ts

def gen_projects(workspace_id: str, teams, users, n_projects: int, history_days: int):
    templates = [
        "Q{q} Roadmap - {area}",
        "{area} Reliability Improvements",
        "Launch: {product} - {quarter}",
        "Ops Intake - {quarter}",
        "Content Calendar - {month}"
    ]
    areas = ["Billing", "Auth", "Onboarding", "Data Platform", "Integrations", "Mobile"]
    products = ["Northstar AI", "Northstar Sync", "Northstar Cloud"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    out = []
    for _ in range(n_projects):
        t = random.choice(teams)
        u = random.choice(users)
        tpl = random.choice(templates)
        name = tpl.format(
            q=random.choice([1,2,3,4]),
            area=random.choice(areas),
            product=random.choice(products),
            quarter=random.choice(quarters),
            month=random.choice(months),
        )
        created_at = random_past_datetime(history_days)
        out.append({
            "project_id": gid(),
            "workspace_id": workspace_id,
            "team_id": t["team_id"],
            "name": name,
            "description": None,
            "privacy": "organization",
            "layout": random.choice(["list", "board"]),
            "status": "active",
            "color": None,
            "created_by": u["user_id"],
            "created_at": iso_ts(created_at),
            "archived_at": None,
        })
    return out

def gen_sections(projects, history_days: int):
    # Simple default workflow; you can vary by project type later
    default = ["Backlog", "In Progress", "Blocked", "Done"]
    out = []
    for p in projects:
        for i, name in enumerate(default):
            out.append({
                "section_id": gid(),
                "project_id": p["project_id"],
                "name": name,
                "sort_order": i,
                "created_at": iso_ts(random_past_datetime(history_days)),
            })
    return out
