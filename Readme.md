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

FL-02 — Prompting Fundamentals on Real Tasks

Overview

This project explores how structured prompt engineering techniques improve AI-assisted backend development. The exercise was completed using a real FastAPI backend task: building a CRUD API with SQLite persistence for managing tasks.

Objective

The goal was to compare a basic prompt with progressively improved prompts and observe how different prompting techniques affect the quality, structure, clarity, and reliability of AI-generated software.

Prompting Techniques

Six prompt iterations were planned:

1. Naive Prompt — Established a baseline using a simple one-line request.
2. Role Assignment — Asked the AI to act as a senior backend engineer.
3. Context & Motivation — Provided project context, learning goals, and future requirements.
4. Few-Shot Examples — Provided examples demonstrating the expected project structure and explanations.
5. Output Structure — Defined a strict format for the AI's response.
6. Step Decomposition — Broke the development task into smaller, sequential steps.

Task

«Build a FastAPI CRUD API with SQLite persistence for managing tasks.»

The generated project included components for database configuration, SQLAlchemy models, Pydantic schemas, API routes, dependencies, requirements, and documentation.

Key Findings

- Adding a specific role improved technical explanations and professional framing.
- Providing context and motivation helped the AI align its response with project goals.
- Few-shot examples improved adherence to the desired format but did not guarantee implementation correctness.
- Explicit output structures made AI responses easier to review.
- Step decomposition helped organize complex software tasks into smaller, verifiable stages.
- AI-generated code still requires human review, testing, and validation regardless of prompt quality.

Cross-Model Evaluation

The final prompt was evaluated across Claude and ChatGPT to compare differences in implementation guidance, reasoning, structure, and failure points.

The exercise demonstrated that effective prompt engineering is not simply about writing longer prompts. The best results came from combining clear requirements, relevant context, examples, structured outputs, and verification steps.

Reusable Prompt Template

A generalized prompt template was created for backend development tasks, including:

- Role and technical expertise
- Project context and motivation
- Functional requirements
- Technical requirements
- Expected project structure
- Implementation steps
- Testing and verification
- Known limitations

Outcome

This exercise developed practical experience in prompt engineering, AI-assisted backend development, output evaluation, and cross-model comparison using a real software engineering task.