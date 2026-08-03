"""
models.py
Data models for the Career & Study Prioritization Agent.

I am not 100% certain which ORM (if any) you'd prefer, so I've kept this
dependency-free using dataclasses + sqlite3, rather than assuming SQLAlchemy.
If you want SQLAlchemy models instead, that's a straightforward swap.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Task:
    id: Optional[int]
    name: str
    category: str          # e.g. "Internship", "Exam", "Technical", "Project"
    priority: str           # "High" | "Medium" | "Low"
    deadline: str            # ISO date string "YYYY-MM-DD"
    duration_minutes: int
    status: str = "Pending"   # "Pending" | "In Progress" | "Completed" | "Overdue"
    description: str = ""
    goal_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "priority": self.priority,
            "deadline": self.deadline,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "description": self.description,
            "goal_id": self.goal_id,
            "created_at": self.created_at,
        }


@dataclass
class Goal:
    id: Optional[int]
    title: str
    description: str = ""
    target_date: Optional[str] = None
    progress_percent: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "target_date": self.target_date,
            "progress_percent": self.progress_percent,
            "created_at": self.created_at,
        }


@dataclass
class DailyPlan:
    id: Optional[int]
    date: str
    available_minutes: int
    planned_task_ids: str      # stored as comma-separated ids in SQLite
    summary: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "available_minutes": self.available_minutes,
            "planned_task_ids": self.planned_task_ids,
            "summary": self.summary,
            "created_at": self.created_at,
        }
