import random
from ..utils.ids import gid
from ..utils.dates import random_past_datetime, iso_ts

def gen_tags(workspace_id: str, n_tags: int, history_days: int):
    base = ["tech-debt", "customer-ask", "security", "launch", "blocked", "urgent", "design", "legal"]
    out = []
    for i in range(n_tags):
        name = base[i % len(base)]
        if i >= len(base):
            name = f"{name}-{i}"
        out.append({
            "tag_id": gid(),
            "workspace_id": workspace_id,
            "name": name,
            "color": None,
            "created_at": iso_ts(random_past_datetime(history_days)),
        })
    return out

def gen_task_tags(tasks, tags):
    out = []
    for t in tasks:
        k = random.choices([0,1,2,3], weights=[0.35,0.4,0.2,0.05])[0]
        for tag in random.sample(tags, k=min(k, len(tags))):
            out.append({"task_id": t["task_id"], "tag_id": tag["tag_id"]})
    return out
