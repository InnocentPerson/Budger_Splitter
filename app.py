from flask import Flask, render_template, request, redirect, url_for
import os
from utils import load_json, save_json, add_roommate, delete_roommate, split_expense, update_balances
from datetime import datetime

app = Flask(__name__)

# ✅ Store uploads inside static so Flask can serve them
app.config["UPLOAD_FOLDER"] = "static/uploads/"

ROOMMATES_FILE = "data/roommates.json"
EXPENSES_FILE = "data/expenses.json"

# Load data at startup
roommates = load_json(ROOMMATES_FILE).get("roommates", [])
expenses = load_json(EXPENSES_FILE).get("expenses", [])

def save_all():
    save_json(ROOMMATES_FILE, {"roommates": roommates})
    save_json(EXPENSES_FILE, {"expenses": expenses})

def calculate_balances():
    """Recalculate balances fresh from expenses every time."""
    balances = {r: 0 for r in roommates}
    for exp in expenses:
        payer = exp["payer"]
        split_dict = exp["split"]
        update_balances(balances, payer, split_dict)
    return balances

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", roommates=roommates)

@app.route("/balances")
def show_balances():
    balances = calculate_balances()
    return render_template("balances.html", balances=balances)

@app.route("/expenses")
def show_expenses():
    sorted_expenses = sorted(expenses, key=lambda e: e.get("date", ""), reverse=True)
    return render_template("expenses.html", expenses=sorted_expenses)

@app.route("/add_roommate", methods=["POST"])
def add_roommate_route():
    name = request.form.get("name")
    if name:
        add_roommate(roommates, name)
        save_all()
    return redirect(url_for("index"))

@app.route("/delete_roommate", methods=["POST"])
def delete_roommate_route():
    name = request.form.get("name")
    if name:
        delete_roommate(roommates, {}, name)
        save_all()
    return redirect(url_for("index"))

@app.route("/add_expense", methods=["POST"])
def add_expense_route():
    name = request.form.get("name")
    amount = float(request.form.get("amount"))
    payer = request.form.get("payer")

    # Handle bill photo upload
    file = request.files.get("bill_photo")
    saved_file = ""
    if file and file.filename:
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        saved_file = file.filename   # ✅ store only filename

    # Split the expense among roommates
    split_dict = split_expense(amount, payer, roommates)

    # Save expense record
    expense_record = {
        "name": name,
        "amount": amount,
        "payer": payer,
        "split": split_dict,
        "bill_photo": saved_file,  # ✅ just filename
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    expenses.append(expense_record)
    save_all()

    return redirect(url_for("show_expenses"))

if __name__ == "__main__":
    app.run(debug=True)
