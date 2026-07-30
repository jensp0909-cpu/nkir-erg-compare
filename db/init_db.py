import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from db.fields import FIELDS

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def init_db(db_path=None):
    db_path = db_path or config.DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        conn.executemany(
            """
            INSERT OR IGNORE INTO field (key, raw_code, display_name, gender, weight_class, age_category)
            VALUES (:key, :raw_code, :display_name, :gender, :weight_class, :age_category)
            """,
            FIELDS,
        )
        conn.commit()
    finally:
        conn.close()

    return db_path


if __name__ == "__main__":
    path = init_db()
    print(f"Initialized database at {path}")
