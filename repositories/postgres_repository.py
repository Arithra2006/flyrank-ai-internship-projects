import sqlite3

from repositories.task_repository import TaskRepository


class SQLiteTaskRepository(TaskRepository):

    def __init__(self):
        self.db_name = "tasks.db"
        self._initialize_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL
            )
        """)

        # Insert sample tasks only if table is empty
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Learn FastAPI", False),
                    ("Build CRUD API", False),
                    ("Connect SQLite Database", False),
                ]
            )

        conn.commit()
        conn.close()

    def get_all(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks ORDER BY id")

        tasks = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return tasks

    def get_by_id(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )

        row = cursor.fetchone()

        conn.close()

        return dict(row) if row else None

    def create(self, task):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task["title"], False)
        )

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return self.get_by_id(task_id)

    def update(self, task_id, updated_task):
        conn = self.get_connection()
        cursor = conn.cursor()

        if "title" in updated_task:
            cursor.execute(
                "UPDATE tasks SET title=? WHERE id=?",
                (updated_task["title"], task_id)
            )

        elif "done" in updated_task:
            cursor.execute(
                "UPDATE tasks SET done=? WHERE id=?",
                (updated_task["done"], task_id)
            )

        else:
            conn.close()
            return self.get_by_id(task_id)

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return None

        conn.close()

        return self.get_by_id(task_id)

    def delete(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE id=?",
            (task_id,)
        )

        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted