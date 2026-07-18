# Task API - FlyRank Backend AI Internship (BE-04)

A CRUD Task Management API built using **FastAPI**, containerized with **Docker**, and connected to **PostgreSQL** with persistent storage.

This project demonstrates replacing an in-memory storage system with a real PostgreSQL repository while keeping the API routes and service layer unchanged.

---

## Features

- Create tasks
- View all tasks
- View task by ID
- Update tasks
- Delete tasks
- PostgreSQL database integration
- Dockerized application and database
- Persistent database storage using Docker volumes
- Environment-based database configuration

---

## Tech Stack

- FastAPI
- Python 3.13
- PostgreSQL 16
- Docker
- Docker Compose
- Psycopg2
- Pydantic

---

## Project Structure

```
task-api/

│
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
│
├── database/
│   └── init.sql
│
├── models/
│   └── task.py
│
├── repositories/
│   ├── task_repository.py
│   ├── memory_repository.py
│   └── postgres_repository.py
│
└── services/
    └── task_service.py
```

---

## Architecture

The application follows a layered architecture:

```
API Routes
      |
      |
Service Layer
      |
      |
Repository Interface
      |
      |
PostgreSQL Repository
      |
      |
PostgreSQL Database
```

The application was originally built using an in-memory repository.

For this assignment, the storage layer was replaced with PostgreSQL without modifying the API routes or service logic.

---

## Environment Configuration

Database credentials are stored using environment variables.

Example `.env`:

```
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpassword
POSTGRES_DB=taskdb

DATABASE_URL=postgresql://taskuser:taskpassword@db:5432/taskdb
```

The `.env` file is ignored by Git.

A safe template is provided:

```
.env.example
```

---

## Running the Application

### Requirements

Install:

- Docker Desktop

---

### Start Application + Database

Run:

```bash
docker compose up --build
```

This starts both:

```
FastAPI Application
        |
        |
PostgreSQL Database
```

The PostgreSQL database uses a Docker volume to preserve data.

---

## API Documentation

After starting the application, open:

```
http://localhost:8000/docs
```

Swagger UI provides interactive API testing.

---

## Database Initialization

The database table is automatically created using:

```
database/init.sql
```

The table contains:

- id
- title
- done

---

## Persistence Verification

Persistence was verified using these steps:

1. Start the application:

```bash
docker compose up
```

2. Create a task using the API:

Endpoint:

```
POST /tasks
```

Example:

```json
{
    "title": "Persistence Test"
}
```

3. Stop containers:

```bash
docker compose down
```

4. Start again:

```bash
docker compose up
```

5. Retrieve tasks:

```
GET /tasks
```

The previously created task was still available after restarting the application and containers.

This confirms that PostgreSQL data persists using the Docker volume.

---

## Repository Switching

Before:

```
API Routes
     |
Service Layer
     |
Memory Repository
```

After:

```
API Routes
     |
Service Layer
     |
PostgreSQL Repository
     |
PostgreSQL Database
```

The repository implementation was replaced while keeping the service layer and API routes unchanged.

This proves that the application follows a clean storage abstraction.

---

## Future Improvements

- Add Redis caching
- Add database indexes
- Analyze queries using EXPLAIN ANALYZE
- Add authentication
- Add automated tests