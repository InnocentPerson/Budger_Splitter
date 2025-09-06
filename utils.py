import json
import os

# ---------- JSON helpers ----------
def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                content = f.read().strip()
                if not content:  # file is empty
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: {file_path} is corrupted. Starting fresh.")
            return {}
    return {}


def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ---------- Roommate Management ----------
def add_roommate(roommates, name):
    if name not in roommates:
        roommates.append(name)
        print(f"{name} added successfully.")
    else:
        print(f"{name} already exists.")

def delete_roommate(roommates, balances, name):
    if name in roommates:
        roommates.remove(name)
        balances.pop(name, None)
        print(f"{name} deleted successfully.")
    else:
        print(f"{name} not found.")

# ---------- Expense Management ----------
def split_expense(amount, payer, roommates):
    split_amount = amount / len(roommates)
    split_dict = {}
    for r in roommates:
        split_dict[r] = 0 if r == payer else split_amount
    return split_dict

def update_balances(balances, payer, split_dict):
    for r, amt in split_dict.items():
        balances[r] = balances.get(r, 0) - amt
        balances[payer] = balances.get(payer, 0) + amt
    return balances
