"""
Personal Purchase Archive

Author: BingleyPro
Copyright: 2026
"""

from flask import Flask, render_template, request
import datetime as dt
import csv, json
from enum import Enum
from typing_extensions import Literal
import sys, os

class InputType(Enum):
    STRING = 1
    FLOAT = 2
    INTEGER = 3
    DATE = 4
    FILE_PATH = 5

#app = Flask(__name__)

class PurchaseArchive:
    def __init__(self):
        self.purchases = []
        self.file_path = ""

    def set_file_path(self, file_path: str):
        self.file_path = file_path
        return

    def load_purchases(self):
        with open(self.file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                name = row['name']
                date = dt.date.strptime(row['purchase_date'], "%d-%m-%Y")
                brand = row['brand']
                category = row['category']
                price = float(row['price'])
                notes = row['notes']

                self.add_purchase(Purchase(name=name, purchase_date=date, category=category, brand=brand, price=price), False)
        return

    def save_purchase(self, purchase: Purchase):
        data = purchase._to_dict()

        with open(self.file_path, mode='a') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        return

    def add_purchase(self, purchase: Purchase, save: bool):
        self.purchases.append(purchase)
        if save:
            self.save_purchase(purchase)
        return

    def edit_purchase(self, old_purchase: Purchase, new_purchase: Purchase) -> bool:
        try:
            self.purchases[self.purchases.index(old_purchase)] = new_purchase
        except ValueError:
            return False
        return True

    def delete_purchase(self, purchase: Purchase) -> bool:
        try:
            self.purchases.remove(purchase)
        except:
            return False
        return True

    def find_purchase(self, name: str|None = None, purchase_date: dt.date|None = None, category: str|None = None, brand: str|None = None, price: float|None = None, notes: list[str]|None = None):
        if name:
            name = name.lower()
        if category:
            category = category.lower()
        if brand:
            brand = brand.lower()
        if price is not None:
            try:
                price = float(price)
            except:
                price = None
                print("Price is in the wrong format, skipping search filter.")
        if notes:
            for note in notes:
                note = note.lower()

        results = []

        for purchase in self.purchases:
            if (
                (name is None or name in purchase.name.lower())
                and (purchase_date is None or purchase.purchase_date == purchase_date)
                and (category is None or purchase.category is None or category in purchase.category.lower())
                and (brand is None or purchase.brand is None or brand in purchase.brand.lower())
                and (price is None or purchase.price == price)
                and (notes is None or purchase.notes is None or notes in purchase.notes)
            ):
                results.append(purchase)

        return results

    def print_purchases(self):
        # Print table of purchases
        print(f"{'Name':<25} {'Brand':<15} {'Price':<10} {'Date':<12}")
        print("-" * 65)

        for purchase in self.purchases:
            brand = purchase.brand or "-"
            price = purchase.price if purchase.price is not None else "-"
            date = str(purchase.purchase_date)

            print(f"{purchase.name:<25} {brand:<15} ${price:<10} {date:<12}")
        return

class Purchase:
    def __init__(self, name: str, purchase_date: dt.date, category: str|None = None, brand: str|None = None, price: float|None = None, notes: list[str]|None = None):
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.purchase_date = purchase_date
        self.notes = notes

    def _to_dict(self):
        return [self.name, self.purchase_date.strftime("%d-%m-%Y"), self.brand, self.category, self.price, self.notes] # TODO: flip purchase_date for saving

def ask_for_input(message: str, input_type: InputType, optional: bool):
    """Prompts the user for input with a given message. Handles validation based on the choosen input type, and enforces input unless optional."""
    user_input = input(message)

    if optional and user_input is (None or ""):
        return None

    match input_type:
        case InputType.STRING:
            if user_input:
                return user_input
            else:
                print("** Invalid input: an input is required. **")
                return ask_for_input(message, input_type, optional)
        case InputType.INTEGER:
            try:
                input_check = int(user_input)
            except:
                print("** Invalid input: enter a valid integer. **")
                return ask_for_input(message, input_type, optional)
            return input_check
        case InputType.FLOAT:
            try:
                input_check = float(user_input)
            except:
                print("** Invalid input: enter a valid floating point number. **")
                return ask_for_input(message, input_type, optional)
            return input_check
        case InputType.DATE:
            # Check if invalid date
            try:
                input_check = dt.date.strptime(user_input, "%d-%m-%Y")
            except:
                print("** Invalid input: enter a valid date (DD-MM-YYYY). **")
                return ask_for_input(message, input_type, optional)
            return input_check
        case InputType.FILE_PATH:
            if os.path.exists(user_input):
                return user_input
            else:
                print("** Invalid input: choosen file path does not exist. **")
                return ask_for_input(message, input_type, optional)
        case _:
            print("Invalid input type.")
            return

def search_and_select_purchase(archive: PurchaseArchive) -> list[Purchase]:
    """Prompts the user to search for each field of data in a purchase, and returns all found purchases as an array."""
    name = ask_for_input("Please enter the product name to search for (if required): ", InputType.STRING, True)
    date = ask_for_input("Please enter the purchase date (DD-MM-YYYY) to search for (if required): ", InputType.DATE, True)
    brand = ask_for_input("Please enter the product's brand (or leave empty) to search for (if required): ", InputType.STRING, True)
    category = ask_for_input("Please enter the product's category (or leave empty) to search for (if required): ", InputType.STRING, True)
    price = ask_for_input("Please enter the product's price (or leave empty) to search for (if required): ", InputType.FLOAT, True)

    purchases = archive.find_purchase(name=name, purchase_date=date, brand=brand, category=category, price=price) # type: ignore
    return purchases

def prompt_and_edit_purchase(archive: PurchaseArchive,current_purchase: Purchase) -> bool:
    """Prompts the user to edit each field of data in a purchase, edits the purchase, and returns the success value."""
    new_name = ask_for_input("Please enter the product name (if you want to edit it): ", InputType.STRING, True) or current_purchase.name
    new_date = ask_for_input("Please enter the purchase date (DD-MM-YYYY) (if you want to edit it): ", InputType.DATE, True) or current_purchase.purchase_date
    new_brand = ask_for_input("Please enter the product's brand (or leave empty) (if you want to edit it): ", InputType.STRING, True) or current_purchase.brand
    new_category = ask_for_input("Please enter the product's category (or leave empty) (if you want to edit it): ", InputType.STRING, True) or current_purchase.category
    new_price = ask_for_input("Please enter the product's price (or leave empty) (if you want to edit it): ", InputType.FLOAT, True) or current_purchase.price

    return archive.edit_purchase(current_purchase, Purchase(name=new_name, purchase_date=new_date, brand=new_brand, category=new_category, price=new_price, notes=current_purchase.notes)) # type: ignore

def display_home_menu():
    print("-----Personal Purchase Archive -----\n")

    ARCHIVE.print_purchases()

    print("\n1. Add a new purchase")
    print("2. Edit an existing purchase")
    print("3. Delete an existing purchase")
    print("4. Load a different archive")
    print("5. Settings")
    print("6. Exit")

    user_input = ask_for_input("Enter your selection: ", InputType.INTEGER, False)
    manage_home_input(user_input)
    return

def choose_purchase(purchases: list[Purchase]) -> Purchase|Literal[False]:
    print("Multiple purchases found, please review below.\n")

    for index, purchase in enumerate(purchases):
        print(f"{purchase.name:<25} {purchase.brand:<15} ${purchase.price:<10} {purchase.purchase_date:<12}")

    user_input = ask_for_input("\nType the corresponding number to select a purchase, or anything else to cancel.", InputType.STRING, True)

    if int(user_input) > 0 and int(user_input) < len(purchases) + 1: # type: ignore
        current_purchase = purchases[int(user_input) - 1] # type: ignore
    else:
        return False
    return current_purchase

def confirm_purchase(purchase: Purchase, action: str) -> bool:
    print("Please confirm the purchase below.\n")
    print(f"{purchase.name:<25} {purchase.brand:<15} ${purchase.price:<10} {purchase.purchase_date:<12}")

    user_input = ask_for_input(f"\nType \"yes\" to confirm, or anything else to cancel {action}: ", InputType.STRING, True)

    return user_input == "yes"

def manage_home_input(user_input):
    match str(user_input):
        case "1":
            # -- Add a new purchase --
            name = ask_for_input("Please enter the product name: ", InputType.STRING, False)
            date = ask_for_input("Please enter the purchase date (DD-MM-YYYY): ", InputType.DATE, False)
            brand = ask_for_input("Please enter the product's brand (or leave empty): ", InputType.STRING, True)
            category = ask_for_input("Please enter the product's category (or leave empty): ", InputType.STRING, True)
            price = ask_for_input("Please enter the product's price (or leave empty): ", InputType.FLOAT, True)

            ARCHIVE.add_purchase(Purchase(name=name, purchase_date=date, brand=brand, category=category, price=price), True) # type: ignore
        case "2":
            # -- Edit an existing purchase --
            purchases = search_and_select_purchase(archive=ARCHIVE)

            if len(purchases) == 0:
                print("No purchases found, please try again.")
            elif len(purchases) == 1:
                if confirm_purchase(purchases[0], "editing"):
                    prompt_and_edit_purchase(ARCHIVE, purchases[0])
                else:
                    print("Editing canceled.")
            elif len(purchases) < 6:
                current_purchase = choose_purchase(purchases)

                if current_purchase:
                    if confirm_purchase(current_purchase, "editing"):
                        prompt_and_edit_purchase(ARCHIVE,current_purchase)
                        print("Purchase edited.")
                    else:
                        print("Editing canceled.")
            else:
                print("Too many purchases matched. Please try again with a stricter match.")
        case "3":
            # -- Delete an existing purchase --
            purchases = search_and_select_purchase(ARCHIVE)

            if len(purchases) == 0:
                print("No purchases found, please try again.")
            elif len(purchases) == 1:
                if confirm_purchase(purchases[0], "deleting"):
                    ARCHIVE.delete_purchase(purchases[0])
                else:
                    print("Deleting canceled.")
            elif len(purchases) < 6:
                current_purchase = choose_purchase(purchases)
                if current_purchase:
                    if confirm_purchase(current_purchase, "deleting"):
                        ARCHIVE.delete_purchase(current_purchase)
                        print("Purchase deleted.")
                    else:
                        print("Deleting canceled.")
            else:
                print("Too many purchases matched. Please try again with a stricter match.")
        case "4":
            # Load a different archive
            user_input = ask_for_input("Please enter the file path of the archive: ", InputType.FILE_PATH, False)
            ARCHIVE.purchases = []
            ARCHIVE.set_file_path(str(user_input))
            ARCHIVE.load_purchases()
        case "5":
            # Settings
            print("\n1. Change default file path")
            print("2. View version information")
            print("3. Return")

            user_input = ask_for_input("Enter your selection: ", InputType.INTEGER, False)

            match str(user_input):
                case "1":
                    user_input = ask_for_input("Please enter the new default file path: ", InputType.FILE_PATH, False)

                    data = {
                        "default_file_path": user_input
                    }
                    with open("settings.json", "w") as file:
                        json.dump(data, file)
                case "2":
                    print("WIP!")
            display_home_menu()
        case "6":
            # Exit
            sys.exit()
        case _:
            print("** Invalid input, try again.**")
    display_home_menu()

# -------------
# Check settings.json for default file. If exists, load it. Otherwise, prompt user for archive.
with open("settings.json", "r") as file:
    data = json.load(file)
    file_path = data["default_file_path"]

    ARCHIVE = PurchaseArchive()

    if os.path.exists(file_path):
        ARCHIVE.set_file_path("example.csv")
        ARCHIVE.load_purchases()
    else:
        user_input = ask_for_input("Please enter the file path of the archive to open: ", InputType.FILE_PATH, False)
        ARCHIVE.set_file_path(str(user_input))
        ARCHIVE.load_purchases()

display_home_menu()

# Flask code
"""
@app.route("/")
def home():
    return render_template("index.html", purchases=purchases)

@app.route("/add", methods=["GET", "POST"])
def add_purchase():
    if request.method == "POST":
        name = request.form["name"]
        brand = request.form["brand"]
        category = request.form["category"]
        price = request.form["price"]
        purchase_date = request.form["purchase_date"]

    return render_template("add.html")
"""

#if __name__ == "__main__":
 #   app.run()