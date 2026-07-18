from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    description="A simple CRUD API built with FastAPI",
    version="1.0"
)

# -----------------------------
# In-memory task list
# -----------------------------
tasks = [
    {"id": 1, "title": "Study FastAPI", "done": False},
    {"id": 2, "title": "Complete Assignment", "done": False},
    {"id": 3, "title": "Watch Movie", "done": True}
]

# -----------------------------
# Request Models
# -----------------------------
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/", summary="API Information")
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "/tasks",
            "/health"
        ]
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}


# -----------------------------
# Get All Tasks
# -----------------------------
@app.get("/tasks", summary="Get All Tasks")
def get_tasks():
    return tasks


# -----------------------------
# Get Task by ID
# -----------------------------
@app.get("/tasks/{task_id}", summary="Get Task By ID")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


# -----------------------------
# Create Task
# -----------------------------
@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(task: TaskCreate):

    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    new_task = {
        "id": max([t["id"] for t in tasks], default=0) + 1,
        "title": title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# -----------------------------
# Update Task
# -----------------------------
@app.put("/tasks/{task_id}", summary="Update Task")
def update_task(task_id: int, updated_task: TaskUpdate):

    for task in tasks:

        if task["id"] == task_id:

            if updated_task.title is not None:

                title = updated_task.title.strip()

                if not title:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Title cannot be empty"
                    )

                task["title"] = title

            if updated_task.done is not None:
                task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


# -----------------------------
# Delete Task
# -----------------------------
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(task_id: int):

    for task in tasks:

        if task["id"] == task_id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )