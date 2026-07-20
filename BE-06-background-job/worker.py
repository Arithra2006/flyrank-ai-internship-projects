import time

from database.database import get_connection
from queue.job_queue import update_job
from services.ai_service import process_prompt


def process_jobs():

    while True:

        conn = get_connection()

        conn.row_factory = __import__("sqlite3").Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM jobs
            WHERE status='queued'
            ORDER BY id
            LIMIT 1
            """
        )

        job = cursor.fetchone()

        conn.close()

        if job:

            job = dict(job)

            print(f"Processing Job {job['id']}")

            update_job(
                job["id"],
                "processing"
            )

            result = process_prompt(
                job["prompt"]
            )

            update_job(
                job["id"],
                "completed",
                result
            )

            print(f"Completed Job {job['id']}")

        else:

            time.sleep(2)


if __name__ == "__main__":

    process_jobs()