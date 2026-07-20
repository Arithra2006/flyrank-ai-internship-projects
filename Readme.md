Task API - FlyRank Backend AI Internship (BE-02)

A CRUD Task Management API built using FastAPI and SQLite.

This project demonstrates replacing an in-memory storage system with a real SQLite database while keeping the API routes and service layer unchanged. The API remains exactly the same, while the storage layer is replaced with a persistent database.

---

Features

- Create tasks
- View all tasks
- View task by ID
- Update tasks
- Delete tasks
- SQLite database integration
- Automatic database creation
- Automatic table creation
- Initial sample tasks inserted only on the first run
- Persistent data storage across server restarts

---

Tech Stack

- FastAPI
- Python 3.13
- SQLite
- sqlite3 (Python Standard Library)
- Pydantic

---

Project Structure

task-api/

│
├── main.py
├── requirements.txt
├── README.md
├── tasks.db          # Automatically created
│
├── models/
│   └── task.py
│
├── repositories/
│   ├── task_repository.py
│   ├── memory_repository.py
│   └── sqlite_repository.py
│
└── services/
    └── task_service.py

---

Architecture

The application follows a layered architecture.

API Routes
      │
      ▼
Service Layer
      │
      ▼
Repository Interface
      │
      ▼
SQLite Repository
      │
      ▼
SQLite Database (tasks.db)

The API layer is completely independent of the database implementation.

The storage layer can be replaced without changing any API endpoints.

---

Why SQLite?

SQLite was chosen because:

- It requires no separate database server.
- The database is stored in a single file ("tasks.db").
- It is lightweight and easy to set up.
- It is ideal for learning SQL and backend development.
- It satisfies the assignment requirement for persistent local storage.

---

Database

The application automatically creates:

tasks.db

on the first run.

It also automatically creates the "tasks" table if it does not already exist.

Schema:

Column| Type
id| INTEGER PRIMARY KEY AUTOINCREMENT
title| TEXT
done| BOOLEAN

If the table is empty, three sample tasks are inserted automatically.

---

Running the Application

Requirements

- Python 3.13+
- pip

Install dependencies:

pip install -r requirements.txt

Start the server:

uvicorn main:app --reload

The database file ("tasks.db") will be created automatically if it does not already exist.

---

API Documentation

After starting the application, open:

http://localhost:8000/docs

Swagger UI provides interactive API documentation and testing.

---

API Endpoints

Method| Endpoint| Description
GET| /tasks| Get all tasks
GET| /tasks/{id}| Get a task by ID
POST| /tasks| Create a new task
PUT| /tasks/{id}| Update a task
DELETE| /tasks/{id}| Delete a task

---

Persistence Verification

Persistence was verified using the following steps:

1. Start the server.
2. Create a new task using:

POST /tasks

3. Stop the server.
4. Restart the server.
5. Retrieve all tasks using:

GET /tasks

The previously created task is still available, confirming that data persists after server restarts.

---

Example SQL Query

The following SQL query was executed to retrieve all tasks:

SELECT * FROM tasks;

---

Database Screenshot

Add a screenshot of your SQLite database viewer (DB Browser for SQLite) here.

Example:

docs/database-screenshot.png

---

Repository Switching

Before:

API Routes
      │
      ▼
Service Layer
      │
      ▼
Memory Repository

After:

API Routes
      │
      ▼
Service Layer
      │
      ▼
SQLite Repository
      │
      ▼
SQLite Database

Only the repository implementation changed. The API routes and service layer remained unchanged.

---

Future Improvements

- Search tasks using SQL ("LIKE")
- Filter completed tasks
- Sort tasks alphabetically
- Add task statistics endpoint
- Add timestamps ("created_at", "updated_at")
- Migrate to PostgreSQL
- Add authentication
- Add automated tests