import sqlite3
from datetime import datetime

DB_FILE = "budget.db"

# ---------- DB Helpers ----------
def get_connection():
    return sqlite3.connect(DB_FILE)

# ---------- Roommate Management ----------
def add_roommate(name):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO roommates (name) VALUES (?)", (name,))
        conn.commit()

def delete_roommate(name):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM roommates WHERE name = ?", (name,))
        conn.commit()

def get_roommates():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM roommates")
        return [row[0] for row in cur.fetchall()]

# ---------- Expense Management ----------
def add_expense(name, amount, payer, bill_photo=""):
    with get_connection() as conn:
        cur = conn.cursor()
        # get payer id
        cur.execute("SELECT id FROM roommates WHERE name = ?", (payer,))
        payer_id = cur.fetchone()
        if not payer_id:
            raise ValueError(f"Payer {payer} not found")
        payer_id = payer_id[0]

        # insert expense
        cur.execute(
            "INSERT INTO expenses (name, amount, payer_id, date, bill_photo) VALUES (?, ?, ?, ?, ?)",
            (name, amount, payer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), bill_photo),
        )
        expense_id = cur.lastrowid

        # split logic
        roommates = get_roommates()
        split_amount = amount / len(roommates)
        for r in roommates:
            cur.execute("SELECT id FROM roommates WHERE name = ?", (r,))
            rid = cur.fetchone()[0]
            share = 0 if r == payer else split_amount
            cur.execute(
                "INSERT INTO expense_splits (expense_id, roommate_id, share) VALUES (?, ?, ?)",
                (expense_id, rid, share),
            )
        conn.commit()

def get_expenses():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, e.name, e.amount, r.name, e.date, e.bill_photo
            FROM expenses e
            JOIN roommates r ON e.payer_id = r.id
            ORDER BY e.date DESC
        """)
        return cur.fetchall()
