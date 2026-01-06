from ..utils.ids import gid
from ..utils.dates import random_past_datetime, iso_ts
import random

def gen_custom_fields(workspace_id: str, users, history_days: int):
    creator = random.choice(users)["user_id"]
    fields = [
        {"custom_field_id": gid(), "workspace_id": workspace_id, "name": "Priority", "field_type": "enum",
         "description": "Task priority", "created_by": creator, "created_at": iso_ts(random_past_datetime(history_days))},
        {"custom_field_id": gid(), "workspace_id": workspace_id, "name": "Effort (pts)", "field_type": "number",
         "description": "Story points / effort estimate", "created_by": creator, "created_at": iso_ts(random_past_datetime(history_days))}
    ]
    return fields

def gen_enum_options(priority_field_id: str):
    opts = [("P0", 0), ("P1", 1), ("P2", 2), ("P3", 3)]
    out = []
    for name, sort in opts:
        out.append({"option_id": gid(), "custom_field_id": priority_field_id, "name": name, "color": None, "sort_order": sort})
    return out

def gen_project_custom_fields(projects, custom_fields):
    out = []
    for p in projects:
        for i, cf in enumerate(custom_fields):
            out.append({
                "project_id": p["project_id"],
                "custom_field_id": cf["custom_field_id"],
                "is_required": 0,
                "sort_order": i,
            })
    return out

def gen_task_custom_field_values(tasks, custom_fields, enum_options_by_field, users, history_days: int):
    out = []
    # simple: assign priority enum to ~70% tasks; effort number to ~50%
    for t in tasks:
        for cf in custom_fields:
            if cf["name"] == "Priority" and random.random() < 0.7:
                opt = random.choice(enum_options_by_field[cf["custom_field_id"]])
                out.append({
                    "task_id": t["task_id"],
                    "custom_field_id": cf["custom_field_id"],
                    "text_value": None,
                    "number_value": None,
                    "date_value": None,
                    "enum_option_id": opt["option_id"],
                    "people_user_id": None,
                    "updated_at": iso_ts(random_past_datetime(history_days)),
                })
            if cf["name"] == "Effort (pts)" and random.random() < 0.5:
                out.append({
                    "task_id": t["task_id"],
                    "custom_field_id": cf["custom_field_id"],
                    "text_value": None,
                    "number_value": float(random.choice([1,2,3,5,8,13])),
                    "date_value": None,
                    "enum_option_id": None,
                    "people_user_id": None,
                    "updated_at": iso_ts(random_past_datetime(history_days)),
                })
    return out
