from dotenv import load_dotenv
from collections import defaultdict
from pathlib import Path
import sqlite3

from src.models.config import load_config
from src.utils.log import get_logger
from src.utils.db import connect, run_schema

from src.generators.users import gen_workspace, gen_teams, gen_users, gen_team_memberships
from src.generators.projects import gen_projects, gen_sections
from src.generators.tasks import gen_tasks, add_subtasks
from src.generators.tags import gen_tags, gen_task_tags
from src.generators.comments import gen_comments
from src.generators.custom_fields import (
    gen_custom_fields, gen_enum_options, gen_project_custom_fields, gen_task_custom_field_values
)

logger = get_logger()


def insert_many(con: sqlite3.Connection, table: str, rows):
    """Insert rows; on failure, rollback and print the first failing row."""
    if not rows:
        return
    cols = list(rows[0].keys())
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
    try:
        con.executemany(sql, ([r[c] for c in cols] for r in rows))
    except sqlite3.IntegrityError:
        con.rollback()  # undo partial executemany inserts
        for r in rows:
            try:
                con.execute(sql, [r[c] for c in cols])
            except sqlite3.IntegrityError:
                print("\nFAILED TABLE:", table)
                print("FAILED ROW:", r)
                raise
        raise


def main():
    load_dotenv()
    cfg = load_config()
    logger.info(f"Writing database to: {cfg.db_path}")

    # robust paths (works no matter where you run from)
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "schema.sql"

    con = connect(cfg.db_path)
    run_schema(con, str(schema_path))

    # 1) workspace
    workspace = gen_workspace()
    insert_many(con, "workspaces", [workspace])

    # 2) teams, users, memberships
    teams = gen_teams(workspace["workspace_id"], cfg.n_teams, cfg.history_days)
    users = gen_users(workspace["workspace_id"], cfg.n_users, cfg.history_days)
    memberships = gen_team_memberships(teams, users, cfg.history_days)

    insert_many(con, "teams", teams)
    insert_many(con, "users", users)
    insert_many(con, "team_memberships", memberships)
    con.commit()

    # 3) projects & sections
    projects = gen_projects(workspace["workspace_id"], teams, users, cfg.n_projects, cfg.history_days)
    sections = gen_sections(projects, cfg.history_days)

    insert_many(con, "projects", projects)
    insert_many(con, "sections", sections)
    con.commit()

    sections_by_project = defaultdict(list)
    for s in sections:
        sections_by_project[s["project_id"]].append(s)

    # 4) tasks & subtasks
    tasks = gen_tasks(
        workspace["workspace_id"],
        projects,
        sections_by_project,
        users,
        cfg.n_tasks,
        cfg.history_days,
    )
    add_subtasks(tasks, pct_subtasks=0.25)

    # IMPORTANT: insert all tasks first with parent_task_id = NULL
    tasks_for_insert = []
    for t in tasks:
        t2 = dict(t)
        t2["parent_task_id"] = None
        tasks_for_insert.append(t2)

    insert_many(con, "tasks", tasks_for_insert)
    con.commit()

    # Then update parent_task_id (ensures FK parent exists)
    parent_updates = [(t["parent_task_id"], t["task_id"]) for t in tasks if t["parent_task_id"] is not None]
    con.executemany("UPDATE tasks SET parent_task_id = ? WHERE task_id = ?", parent_updates)
    con.commit()

    # 5) tags + task_tags
    tags = gen_tags(workspace["workspace_id"], cfg.n_tags, cfg.history_days)
    insert_many(con, "tags", tags)
    task_tags = gen_task_tags(tasks, tags)
    insert_many(con, "task_tags", task_tags)
    con.commit()

    # 6) comments
    comments = gen_comments(tasks, users, cfg.max_comments_per_task, cfg.history_days)
    insert_many(con, "comments", comments)
    con.commit()

    # 7) custom fields
    custom_fields = gen_custom_fields(workspace["workspace_id"], users, cfg.history_days)
    insert_many(con, "custom_field_definitions", custom_fields)

    enum_options_by_field = {}
    for cf in custom_fields:
        if cf["field_type"] == "enum" and cf["name"] == "Priority":
            opts = gen_enum_options(cf["custom_field_id"])
            enum_options_by_field[cf["custom_field_id"]] = opts
            insert_many(con, "custom_field_enum_options", opts)

    project_cfs = gen_project_custom_fields(projects, custom_fields)
    insert_many(con, "project_custom_fields", project_cfs)

    tcfv = gen_task_custom_field_values(tasks, custom_fields, enum_options_by_field, users, cfg.history_days)
    insert_many(con, "task_custom_field_values", tcfv)
    con.commit()

    con.close()
    logger.info("Done.")


if __name__ == "__main__":
    main()
