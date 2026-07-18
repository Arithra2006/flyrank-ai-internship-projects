import psycopg2
from psycopg2.extras import RealDictCursor

from repositories.task_repository import TaskRepository

import os
from dotenv import load_dotenv

load_dotenv()


class PostgresTaskRepository(TaskRepository):

    def __init__(self):

        self.connection_url = os.getenv(
            "DATABASE_URL"
        )


    def get_connection(self):

        return psycopg2.connect(
            self.connection_url
        )


    def get_all(self):

        conn = self.get_connection()
        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            "SELECT * FROM tasks ORDER BY id"
        )

        tasks = cursor.fetchall()

        cursor.close()
        conn.close()

        return tasks



    def get_by_id(self, task_id):

        conn = self.get_connection()
        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            "SELECT * FROM tasks WHERE id=%s",
            (task_id,)
        )

        task = cursor.fetchone()

        cursor.close()
        conn.close()

        return task



    def create(self, task):

        conn = self.get_connection()
        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            INSERT INTO tasks(title, done)
            VALUES(%s, %s)
            RETURNING *
            """,
            (
                task["title"],
                False
            )
        )

        new_task = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return new_task



    def update(self, task_id, updated_task):

        conn = self.get_connection()
        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )


        if "title" in updated_task:

            cursor.execute(
                """
                UPDATE tasks
                SET title=%s
                WHERE id=%s
                RETURNING *
                """,
                (
                    updated_task["title"],
                    task_id
                )
            )

        elif "done" in updated_task:

            cursor.execute(
                """
                UPDATE tasks
                SET done=%s
                WHERE id=%s
                RETURNING *
                """,
                (
                    updated_task["done"],
                    task_id
                )
            )

        else:
            return self.get_by_id(task_id)


        task = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return task



    def delete(self, task_id):

        conn = self.get_connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id=%s
            """,
            (task_id,)
        )

        deleted = cursor.rowcount > 0

        conn.commit()

        cursor.close()
        conn.close()

        return deleted