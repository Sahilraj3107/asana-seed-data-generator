from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    db_path: str
    n_users: int
    n_teams: int
    n_projects: int
    n_tasks: int
    n_tags: int
    max_comments_per_task: int
    history_days: int

def load_config() -> Config:
    def geti(key: str, default: int) -> int:
        return int(os.getenv(key, str(default)))

    return Config(
        db_path=os.getenv("DB_PATH", "output/asana_simulation.sqlite"),
        n_users=geti("N_USERS", 2000),
        n_teams=geti("N_TEAMS", 40),
        n_projects=geti("N_PROJECTS", 120),
        n_tasks=geti("N_TASKS", 50000),
        n_tags=geti("N_TAGS", 80),
        max_comments_per_task=geti("MAX_COMMENTS_PER_TASK", 3),
        history_days=geti("HISTORY_DAYS", 180),
    )
