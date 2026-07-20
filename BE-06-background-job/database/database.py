import sqlite3


DATABASE = "database/jobs.db"


def get_connection():

    return sqlite3.connect(DATABASE)


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT
        )
        """
    )

    conn.commit()
    conn.close()