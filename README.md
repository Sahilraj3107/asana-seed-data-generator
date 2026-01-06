# Asana RL Seed Data Generator (SQLite)

Generates a realistic Asana-like workspace dataset for reinforcement-learning (RL) / computer-use agent evaluation. The output is a SQLite database file (`output/asana_simulation.sqlite`) containing tables for workspaces, teams, users, projects, sections, tasks/subtasks, comments, custom fields, tags, and associations.

## What this project contains
- **Relational schema** in `schema.sql` with primary/foreign keys (FK checks enabled in SQLite).
- **Python generators** in `src/generators/` for each entity.
- **Configurable data scale** using `.env` (users/projects/tasks counts, time history, etc.).
- **Output database** written to `output/asana_simulation.sqlite`.

## Repository structure
```
├── README.md
├── requirements.txt
├── schema.sql
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── generators/
│   ├── models/
│   ├── utils/
│   └── scrapers/ (optional)
└── output/
    └── asana_simulation.sqlite  (generated)
```

## Requirements
- Python 3.10+ recommended
- SQLite (optional, for CLI inspection)

## Setup (Windows)
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
```

## Setup (macOS/Linux)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

## Configure dataset size
Edit `.env` to control dataset scale:
```env
DB_PATH=output/asana_simulation.sqlite

N_USERS=2000
N_TEAMS=40
N_PROJECTS=120
N_TASKS=50000
N_TAGS=80
MAX_COMMENTS_PER_TASK=3
HISTORY_DAYS=180
```

## Generate the SQLite database
From the repository root:
```bash
python -m src.main
```

This will create:
- `output/asana_simulation.sqlite`

## Inspect the database
### Option A: SQLite CLI
```bash
sqlite3 output/asana_simulation.sqlite
.tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM projects;
SELECT COUNT(*) FROM tasks;
.quit
```

### Option B: GUI
Open the `.sqlite` file with DB Browser for SQLite / Beekeeper Studio.

## Data model (high level)
The dataset simulates a company workspace with:
- **workspaces** → **teams** → **projects** → **sections** → **tasks**
- **subtasks** are represented via `tasks.parent_task_id` (task hierarchy).
- **comments** represent task discussion.
- **custom fields** are modeled using:
  - `custom_field_definitions`
  - `project_custom_fields` (which fields are enabled per project)
  - `task_custom_field_values` (values per task)
- **tags** are modeled via `tags` and `task_tags`.

## Notes on integrity and consistency
- SQLite foreign key enforcement is enabled in code (`PRAGMA foreign_keys = ON`).
- Tasks are inserted first, then `parent_task_id` is updated to avoid FK issues for subtasks.
- Timestamps are generated to be logically consistent (e.g., `updated_at >= created_at`).

## Common issues
### `cp` not recognized on Windows
Use:
```bat
copy .env.example .env
```

### Relative import errors
Run the entry point as a module:
```bash
python -m src.main
```

## Development tips
- Start small (`N_TASKS=5000`) to iterate quickly, then scale up.
- Add sanity checks in `src/utils/` (e.g., counts, overdue tasks, unassigned tasks) as you improve realism.

