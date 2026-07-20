# FlyRank Backend AI Internship - BE-06 Background Job API

## Overview

This project demonstrates background job processing using FastAPI and SQLite.

Instead of waiting for a slow task to finish, the API immediately accepts the request and returns a Job ID. A background worker processes the task, while clients can check its status using a separate endpoint.

---

## Features

- Background job processing
- SQLite database
- Queue-based architecture
- Worker process
- Job status tracking
- REST API using FastAPI

---

## Tech Stack

- Python 3.13
- FastAPI
- SQLite
- Pydantic
- Uvicorn
- Python-dotenv

---

## Project Structure

```
BE-06-background-job/

│
├── main.py
├── worker.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── database/
│   ├── database.py
│   └── jobs.db
│
├── models/
│   ├── __init__.py
│   └── job.py
│
├── queue/
│   ├── __init__.py
│   └── job_queue.py
│
└── services/
    ├── __init__.py
    └── ai_service.py
```

---

## Workflow

```
Client
   │
   ▼
POST /jobs
   │
   ▼
Job stored in SQLite
   │
   ▼
202 Accepted
   │
   ▼
Background Worker
   │
   ▼
Processes Job
   │
   ▼
Updates Database
   │
   ▼
GET /jobs/{id}
```

---

## API Endpoints

### Create Job

```
POST /jobs
```

Example request:

```json
{
    "prompt": "Explain Artificial Intelligence"
}
```

Response:

```json
{
    "job_id": 1,
    "status": "queued"
}
```

Status Code:

```
202 Accepted
```

---

### Check Job Status

```
GET /jobs/{job_id}
```

Example response:

```json
{
    "id": 1,
    "prompt": "Explain Artificial Intelligence",
    "status": "completed",
    "result": "AI Response: Explain Artificial Intelligence"
}
```

---

## Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn main:app --reload
```

Run the worker (in another terminal):

```bash
python worker.py
```

Open Swagger:

```
http://127.0.0.1:8000/docs
```

---

## Future Improvements

- Retry failed jobs
- Job cancellation
- Redis queue
- Celery workers
- Multiple workers
- Real AI model integration
- Docker support