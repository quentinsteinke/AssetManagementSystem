import sqlite3
import os


def check_db_schema():
    db_path = '..\\app\\Databases\\3d_project_database.db'
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), db_path))
    print(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        print("\n")
        print(f"- {table_name}")
        cursor.execute("PRAGMA table_info({})".format(table_name))
        items = cursor.fetchall()
        for item in items:
            print(f"---- {item}")

    conn.close()


if __name__ == '__main__':
    check_db_schema()