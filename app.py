from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Store uploads inside static so Flask can serve them
app.config["UPLOAD_FOLDER"] = "static/uploads/"
DB_FILE = "data/budget.db"  # ✅ correct path to your DB


# ---------- DB Helpers ----------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------- Routes ----------
@app.route("/")
def index():
    with get_db() as conn:
        roommates = conn.execute("SELECT * FROM roommates").fetchall()
    return render_template("index.html", roommates=roommates)


@app.route("/balances")
def show_balances():
    query = """
    SELECT r.name,
           COALESCE(SUM(CASE WHEN r.id = e.payer_id THEN es.share ELSE -es.share END), 0) AS balance
    FROM roommates r
    LEFT JOIN expense_splits es ON r.id = es.roommate_id
    LEFT JOIN expenses e ON es.expense_id = e.id
    GROUP BY r.id, r.name
    """
    with get_db() as conn:
        balances = conn.execute(query).fetchall()
    return render_template("balances.html", balances=balances)


@app.route("/expenses")
def show_expenses():
    with get_db() as conn:
        expenses = conn.execute("""
            SELECT e.*, r.name AS payer_name
            FROM expenses e
            JOIN roommates r ON e.payer_id = r.id
            ORDER BY e.date DESC
        """).fetchall()
    return render_template("expenses.html", expenses=expenses)


@app.route("/add_roommate", methods=["POST"])
def add_roommate_route():
    name = request.form.get("name")
    if name:
        with get_db() as conn:
            try:
                conn.execute("INSERT INTO roommates (name) VALUES (?)", (name,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # roommate already exists
    return redirect(url_for("index"))


@app.route("/delete_roommate", methods=["POST"])
def delete_roommate_route():
    name = request.form.get("name")
    if name:
        with get_db() as conn:
            conn.execute("DELETE FROM roommates WHERE name = ?", (name,))
            conn.commit()
    return redirect(url_for("index"))


@app.route("/add_expense", methods=["POST"])
def add_expense_route():
    name = request.form.get("name")
    amount = float(request.form.get("amount"))
    payer_id = int(request.form.get("payer"))  # payer is roommate.id

    # Handle bill photo upload
    file = request.files.get("bill_photo")
    saved_file = ""
    if file and file.filename:
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        saved_file = file.filename  # only store filename

    with get_db() as conn:
        # Insert expense
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO expenses (name, amount, payer_id, date, bill_photo)
            VALUES (?, ?, ?, ?, ?)
        """, (name, amount, payer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), saved_file))
        expense_id = cur.lastrowid

        # Split expense equally among roommates
        roommates = conn.execute("SELECT id FROM roommates").fetchall()
        split_amount = amount / len(roommates)
        for r in roommates:
            conn.execute("""
                INSERT INTO expense_splits (expense_id, roommate_id, share)
                VALUES (?, ?, ?)
            """, (expense_id, r["id"], split_amount))

        conn.commit()

    return redirect(url_for("show_expenses"))


if __name__ == "__main__":
    app.run(debug=True)
