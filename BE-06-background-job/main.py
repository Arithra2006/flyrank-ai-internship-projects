from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from database.database import initialize_database
from models.job import JobRequest
from queue.job_queue import create_job, get_job


app = FastAPI(
    title="Background Job API",
    description="Background Job Processing with FastAPI",
    version="1.0"
)


# -----------------------------
# Initialize Database
# -----------------------------

initialize_database()


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Background Job API Running"
    }


# -----------------------------
# Create Job
# -----------------------------

@app.post(
    "/jobs",
    status_code=status.HTTP_202_ACCEPTED
)
def submit_job(job: JobRequest):

    job_id = create_job(job.prompt)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "job_id": job_id,
            "status": "queued"
        }
    )


# -----------------------------
# Get Job Status
# -----------------------------

@app.get("/jobs/{job_id}")
def job_status(job_id: int):

    job = get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job