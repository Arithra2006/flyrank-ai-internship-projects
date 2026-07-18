# Task API

A simple CRUD API built using FastAPI.

## Features

- Create Tasks
- Read All Tasks
- Read Single Task
- Update Task
- Delete Task
- Health Check Endpoint
- Swagger UI Documentation

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn main:app --reload
```

The server will start at:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

## Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | / | API Information |
| GET | /health | Health Check |
| GET | /tasks | Get All Tasks |
| GET | /tasks/{id} | Get Single Task |
| POST | /tasks | Create Task |
| PUT | /tasks/{id} | Update Task |
| DELETE | /tasks/{id} | Delete Task |

## Example POST Request

```json
{
    "title": "Buy Milk"
}
```

## Example Response

```json
{
    "id":4,
    "title":"Buy Milk",
    "done":false
}
```

## Technologies Used

- Python
- FastAPI
- Uvicorn
- Swagger UI