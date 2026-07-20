from database.database import get_connection


def create_job(prompt: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO jobs(prompt, status)
        VALUES(?, ?)
        """,
        (prompt, "queued")
    )

    job_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return job_id


def get_job(job_id: int):

    conn = get_connection()

    conn.row_factory = __import__("sqlite3").Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM jobs
        WHERE id=?
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    conn.close()

    if job:
        return dict(job)

    return None


def update_job(job_id: int, status: str, result: str = None):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET status=?, result=?
        WHERE id=?
        """,
        (
            status,
            result,
            job_id
        )
    )

    conn.commit()
    conn.close()