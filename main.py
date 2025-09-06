
# ONLY FOR CLI , ONCE FLASK IS USED ALL THE INPUT ARE HANDLED BY THE HTML THROUGH WEB , NO NEED OF CLI NOW 
import os
from utils import load_json, save_json, add_roommate, delete_roommate, split_expense, update_balances

ROOMMATES_FILE = "data/roommates.json"
EXPENSES_FILE = "data/expenses.json"
UPLOAD_FOLDER = "uploads/"

# Load data
roommates = load_json(ROOMMATES_FILE).get("roommates", [])
expenses = load_json(EXPENSES_FILE).get("expenses", [])
balances = {r: 0 for r in roommates}

# ---------- Helper Functions ----------
def save_all():
    save_json(ROOMMATES_FILE, {"roommates": roommates})
    save_json(EXPENSES_FILE, {"expenses": expenses})

def add_expense():
    name = input("Enter expense name: ")
    try:
        amount = float(input("Enter total amount: "))
    except ValueError:
        print("Invalid amount.")
        return
    
    print("Roommates:", roommates)
    payer = input("Who paid? ")
    if payer not in roommates:
        print("Payer not found.")
        return
    
    # Optional bill upload
    bill_photo = input("Enter bill file path (or leave empty): ").strip()
    saved_file = ""
    if bill_photo:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        try:
            file_name = os.path.basename(bill_photo)
            saved_file = os.path.join(UPLOAD_FOLDER, file_name)
            with open(bill_photo, "rb") as fsrc, open(saved_file, "wb") as fdst:
                fdst.write(fsrc.read())
            print(f"Bill saved to {saved_file}")
        except Exception as e:
            print("Failed to save bill:", e)
    
    split_dict = split_expense(amount, payer, roommates)
    update_balances(balances, payer, split_dict)
    
    expense_record = {
        "name": name,
        "amount": amount,
        "payer": payer,
        "split": split_dict,
        "bill_photo": saved_file
    }
    expenses.append(expense_record)
    save_all()
    print("Expense added successfully!")

def show_balances():
    print("\n--- Current Balances ---")
    for r, amt in balances.items():
        print(f"{r}: {amt:.2f}")
    print("------------------------\n")

def show_expenses():
    print("\n--- Expense History ---")
    for e in expenses:
        print(f"{e['name']} | Paid by: {e['payer']} | Amount: {e['amount']:.2f}")
        if e['bill_photo']:
            print(f"Bill: {e['bill_photo']}")
    print("----------------------\n")

def manage_roommates():
    print("1. Add Roommate\n2. Delete Roommate")
    choice = input("Choice: ")
    if choice == "1":
        name = input("Enter name to add: ")
        add_roommate(roommates, name)
        balances[name] = 0
    elif choice == "2":
        name = input("Enter name to delete: ")
        delete_roommate(roommates, balances, name)
    save_all()

# ---------- Main Loop ----------
while True:
    print("\n--- Roommate Budget Splitter ---")
    print("1. Add Expense")
    print("2. Show Balances")
    print("3. Show Expense History")
    print("4. Manage Roommates")
    print("5. Exit")
    choice = input("Select option: ")
    
    if choice == "1":
        add_expense()
    elif choice == "2":
        show_balances()
    elif choice == "3":
        show_expenses()
    elif choice == "4":
        manage_roommates()
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid choice.")
