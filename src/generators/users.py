from faker import Faker
import random
from ..utils.ids import gid
from ..utils.dates import random_past_datetime, iso_ts

fake = Faker()

def gen_workspace():
    return {
        "workspace_id": gid(),
        "name": "Northstar SaaS, Inc.",
        "domain": "northstarsaas.com",
        "is_organization": 1,
        "created_at": iso_ts(random_past_datetime(900)),
    }

def gen_teams(workspace_id: str, n_teams: int, history_days: int):
    team_names = [
        "Core Platform", "Billing & Subscriptions", "Data Engineering", "Security",
        "Product Marketing", "Demand Gen", "Content & Creative",
        "Sales Ops", "Customer Support Ops", "IT Operations", "People Ops"
    ]
    out = []
    for i in range(n_teams):
        name = team_names[i % len(team_names)]
        if i >= len(team_names):
            name = f"{name} ({i//len(team_names)+1})"
        out.append({
            "team_id": gid(),
            "workspace_id": workspace_id,
            "name": name,
            "description": None,
            "visibility": "organization",
            "created_at": iso_ts(random_past_datetime(history_days)),
        })
    return out

def gen_users(workspace_id: str, n_users: int, history_days: int):
    depts = ["Engineering", "Marketing", "Operations", "Sales", "Finance", "People"]
    out = []
    for _ in range(n_users):
        full_name = fake.name()
        email = fake.unique.email()
        out.append({
            "user_id": gid(),
            "workspace_id": workspace_id,
            "full_name": full_name,
            "email": email,
            "title": fake.job(),
            "department": random.choice(depts),
            "location": fake.city(),
            "is_active": 1,
            "role": "member",
            "created_at": iso_ts(random_past_datetime(900)),
        })
    return out

def gen_team_memberships(teams, users, history_days: int):
    out = []
    for u in users:
        # 1-3 teams per user
        k = random.choices([1,2,3], weights=[0.7,0.25,0.05])[0]
        for t in random.sample(teams, k=min(k, len(teams))):
            out.append({
                "team_id": t["team_id"],
                "user_id": u["user_id"],
                "is_team_admin": 1 if random.random() < 0.03 else 0,
                "joined_at": iso_ts(random_past_datetime(history_days)),
            })
    return out
