from pydantic import BaseModel


class JobRequest(BaseModel):
    prompt: str


class JobResponse(BaseModel):
    job_id: int
    status: str


class JobStatus(BaseModel):
    job_id: int
    status: str
    result: str | None = None