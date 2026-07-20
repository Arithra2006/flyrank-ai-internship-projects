from fastapi import FastAPI, HTTPException, status

from models.task import TaskCreate, TaskUpdate
from repositories.sqlite_repository import SQLiteTaskRepository
from services.task_service import TaskService


app = FastAPI(
    title="Task API",
    description="A simple CRUD API built with FastAPI",
    version="1.0"
)


# -----------------------------
# Repository + Service Setup
# -----------------------------

repository = SQLiteTaskRepository()
service = TaskService(repository)



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

    return service.get_tasks()



# -----------------------------
# Get Task By ID
# -----------------------------

@app.get("/tasks/{task_id}", summary="Get Task By ID")
def get_task(task_id: int):

    task = service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task



# -----------------------------
# Create Task
# -----------------------------

@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Create Task"
)
def create_task(task: TaskCreate):

    new_task = service.create_task(task)

    if not new_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    return new_task



# -----------------------------
# Update Task
# -----------------------------

@app.put("/tasks/{task_id}", summary="Update Task")
def update_task(task_id: int, updated_task: TaskUpdate):

    task = service.update_task(
        task_id,
        updated_task
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task



# -----------------------------
# Delete Task
# -----------------------------

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task"
)
def delete_task(task_id: int):

    deleted = service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return