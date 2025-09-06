import sqlite3
import os

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

DB_FILE = "data/budget.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS roommates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    payer_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    bill_photo TEXT,
    FOREIGN KEY (payer_id) REFERENCES roommates(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expense_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    roommate_id INTEGER NOT NULL,
    share REAL NOT NULL,
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (roommate_id) REFERENCES roommates(id) ON DELETE CASCADE
)
""")

conn.commit()
conn.close()
print("Database created successfully!")
