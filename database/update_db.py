"""
Database Schema Upgrade - Adds rich medical detail columns.
"""
import sqlite3
import os

DB_PATH = "database/health_library.db"

NEW_COLUMNS = [
    ("overview", "TEXT"),
    ("symptoms", "TEXT"),
    ("medicines", "TEXT"),
    ("causes", "TEXT"),
    ("prevention", "TEXT"),
    ("when_to_see_doctor", "TEXT"),
    ("home_remedies", "TEXT"),
]

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("Upgrading database schema...")
    for col_name, col_type in NEW_COLUMNS:
        try:
            cursor.execute(f"ALTER TABLE diseases ADD COLUMN {col_name} {col_type}")
            print(f"  + Added '{col_name}' column.")
        except sqlite3.OperationalError:
            print(f"  - '{col_name}' column already exists.")
    conn.commit()
    conn.close()
    print("Schema upgrade complete!")

if __name__ == "__main__":
    update_schema()
