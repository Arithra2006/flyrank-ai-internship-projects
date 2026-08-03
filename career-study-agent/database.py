"""
database.py
SQLite persistence layer for the Career & Study Prioritization Agent.

Run this file directly to (re)create the database with the schema and
some example seed data:

    python database.py

Note: the seed data below is illustrative placeholder data (matching the
examples in the project spec), not real data about any actual person.
"""

import sqlite3
import os
from datetime import date, timedelta
from contextlib import contextmanager

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "tasks.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    target_date TEXT,
    progress_percent INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('High','Medium','Low')),
    deadline TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending','In Progress','Completed','Overdue')),
    description TEXT DEFAULT '',
    goal_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS daily_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    available_minutes INTEGER NOT NULL,
    planned_task_ids TEXT NOT NULL,
    summary TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
"""


@contextmanager
def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

def add_goal(title, description="", target_date=None, progress_percent=0):
    from datetime import datetime
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO goals (title, description, target_date, progress_percent, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, description, target_date, progress_percent, datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_goals():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM goals ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def update_goal_progress(goal_id, progress_percent):
    with get_connection() as conn:
        conn.execute(
            "UPDATE goals SET progress_percent = ? WHERE id = ?",
            (progress_percent, goal_id),
        )


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def add_task(name, category, priority, deadline, duration_minutes,
             status="Pending", description="", goal_id=None):
    from datetime import datetime
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (name, category, priority, deadline, duration_minutes, "
            "status, description, goal_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, category, priority, deadline, duration_minutes, status,
             description, goal_id, datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_tasks(status=None):
    with get_connection() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY deadline", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tasks ORDER BY deadline").fetchall()
        return [dict(r) for r in rows]


def get_task_by_id(task_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def get_deadlines(within_days=None):
    """Return tasks sorted by deadline, optionally filtered to the next N days."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status != 'Completed' ORDER BY deadline"
        ).fetchall()
        tasks = [dict(r) for r in rows]
    if within_days is not None:
        cutoff = date.today() + timedelta(days=within_days)
        tasks = [t for t in tasks if _safe_date(t["deadline"]) and _safe_date(t["deadline"]) <= cutoff]
    return tasks


def _safe_date(s):
    try:
        y, m, d = map(int, s.split("-"))
        return date(y, m, d)
    except Exception:
        return None


def update_task_status(task_id, status):
    valid = {"Pending", "In Progress", "Completed", "Overdue"}
    if status not in valid:
        raise ValueError(f"Invalid status '{status}'. Must be one of {valid}")
    with get_connection() as conn:
        cur = conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        if cur.rowcount == 0:
            raise ValueError(f"No task found with id {task_id}")


def mark_overdue_tasks():
    """Flip Pending tasks whose deadline has passed to Overdue. Run this at the
    start of a session; the agent should never silently invent overdue status."""
    today_str = date.today().isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET status = 'Overdue' "
            "WHERE status = 'Pending' AND deadline < ?",
            (today_str,),
        )


# ---------------------------------------------------------------------------
# Daily plans
# ---------------------------------------------------------------------------

def save_daily_plan(plan_date, available_minutes, planned_task_ids, summary=""):
    from datetime import datetime
    ids_str = ",".join(str(i) for i in planned_task_ids)
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO daily_plans (date, available_minutes, planned_task_ids, summary, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (plan_date, available_minutes, ids_str, summary, datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_daily_plans(limit=10):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_plans ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Seed data (illustrative placeholder data only)
# ---------------------------------------------------------------------------

def seed_example_data():
    if get_goals() or get_tasks():
        print("Database already has data — skipping seed to avoid duplicates.")
        return

    g1 = add_goal("Clear competitive examination", "Bank exam prep", "2026-09-01", 40)
    g2 = add_goal("Improve Python backend skills", "FastAPI, databases, APIs", "2026-10-01", 55)
    g3 = add_goal("Build AI/ML projects", "Portfolio projects for job applications", "2026-12-01", 20)
    g4 = add_goal("Complete internship assignments", "FlyRank internship deliverables", "2026-08-30", 60)

    add_task("Complete internship assignment", "Internship", "High", "2026-08-05", 90,
              description="FlyRank assignment submission", goal_id=g4)
    add_task("Quantitative Aptitude Practice", "Exam", "High", "2026-08-10", 60,
              description="Practice set for bank exam", goal_id=g1)
    add_task("Revise FastAPI", "Technical", "Medium", "2026-08-15", 45,
              description="Review async endpoints and dependency injection", goal_id=g2)
    add_task("Build ML project demo", "Project", "Medium", "2026-08-20", 120,
              description="Portfolio project for job applications", goal_id=g3)
    add_task("Mock interview practice", "Technical", "Low", "2026-08-25", 30,
              description="Behavioral + technical mock interview", goal_id=g2)

    print("Seed data inserted.")


if __name__ == "__main__":
    init_db()
    mark_overdue_tasks()
    seed_example_data()
    print(f"Database ready at: {DB_PATH}")
