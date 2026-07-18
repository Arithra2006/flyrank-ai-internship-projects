# Task API

A simple RESTful Task Management API built using **FastAPI**. This project demonstrates CRUD (Create, Read, Update, Delete) operations using an in-memory task list without a database.

## Features

- Create a new task
- View all tasks
- View a task by ID
- Update an existing task
- Delete a task
- Health check endpoint
- Interactive Swagger UI documentation

## Technologies Used

- Python 3
- FastAPI
- Uvicorn
- Pydantic

## Installation

Clone the repository:

```bash
git clone https://github.com/Arithra2006/flyrank-ai-internship-projects.git
```

Go to the project folder:

```bash
cd flyrank-ai-internship-projects
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project

```bash
uvicorn main:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{task_id}` | Get a task by ID |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Example Request

**POST /tasks**

```json
{
    "title": "Buy Milk"
}
```

## Example Response

```json
{
    "id": 4,
    "title": "Buy Milk",
    "done": false
}
```

## Project Structure

```
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Author

**Arithra Mayur**