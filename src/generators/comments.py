import random
from ..utils.ids import gid
from ..utils.dates import random_past_datetime, iso_ts

def gen_comments(tasks, users, max_comments_per_task: int, history_days: int):
    bodies = [
        "Blocked on review from Legal.",
        "Can someone confirm the acceptance criteria?",
        "Deployed to staging; monitoring metrics.",
        "Customer reported this again—raising priority.",
        "I’ll take this after finishing the current task."
    ]
    out = []
    for t in tasks:
        k = random.randint(0, max_comments_per_task)
        for _ in range(k):
            out.append({
                "comment_id": gid(),
                "task_id": t["task_id"],
                "author_id": random.choice(users)["user_id"],
                "body": random.choice(bodies),
                "created_at": iso_ts(random_past_datetime(history_days)),
            })
    return out
