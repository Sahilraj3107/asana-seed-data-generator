# Asana RL Seed Dataset (SQLite)

Generates a realistic-ish Asana-like workspace dataset into a SQLite file for RL environment seeding.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
copy .env.example .env
