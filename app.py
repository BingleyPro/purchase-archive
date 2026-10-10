"""
Personal Purchase Archive

Author: BingleyPro
Copyright: 2026
"""

from __future__ import annotations
import datetime as dt
import json
from enum import Enum
from typing_extensions import Literal
import sys, os
import math

class InputType(Enum):
    STRING = 1
    FLOAT = 2
    INTEGER = 3
    DATE = 4
    FILE_PATH = 5
    FILE_PATH_NOT_EXIST = 6

class PurchaseArchive:
    def __init__(self):
        self.purchases = []
        self.file_path = ""
        self.next_id = 1

    def set_file_path(self, file_path: str):
        self.file_path = file_path
        return

    def get_next_id(self) -> int:
        purchase_id = self.next_id
        self.next_id += 1
        return purchase_id

    def load_purchases(self) -> bool:
        if not os.path.isfile(self.file_path):
            print(f"Error: {self.file_path} is invalid, archive file may have been moved.")
            return False
        
        with open(self.file_path, mode='r', newline='') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(f"The file {self.file_path} is not in JSON format.")
                return False

        loaded_purchases = []
        try:
            # TODO: Maybe use .get()?
            for i in data.get("purchases", []):
                id = i['id']
                name = i['name']
                date = dt.date.strptime(i['purchase_date'], "%d-%m-%Y")
                brand = i['brand']
                category = i['category']
                price = i['price']
                if price is not None:
                    price = float(price)
                notes = i['notes']
                tags = i['tags']
                files = i['files']

                loaded_purchases.append(Purchase(id=id, name=name, purchase_date=date, category=category, brand=brand, price=price, notes=notes, tags=tags, files=files))
        except KeyError:
            print("There is an error in the JSON formatting, and purchases could not be loaded.")
            loaded_purchases = []
            return False

        self.purchases = loaded_purchases

        stored_id = data.get("metadata", {}).get("next_id", None)
        minimum_id = max((purchase.id for purchase in loaded_purchases), default=0) + 1

        if stored_id is not None:
            self.next_id = max(int(stored_id), minimum_id)
        else:
            self.next_id = minimum_id
        return True

    def save_to_file(self):
        purchases = []

        for purchase in self.purchases:
            purchases.append(purchase._to_dict())

        if not os.path.isfile(self.file_path):
            print(f"Error: {self.file_path} is invalid, archive file may have been moved.")
            return False
        
        with open(self.file_path, mode='r', newline='') as file:
            try:
                old_data = json.load(file)
            except json.JSONDecodeError:
                print(f"The file {self.file_path} is not in JSON format.")
                return False

        new_data = {
            "metadata": {
                "archive_name": old_data.get("metadata", {}).get("archive_name", ""),
                "next_id": self.next_id
            },
            "backup_file_path": old_data.get("backup_file_path", ""),
            "purchases": purchases
        }

        with open(self.file_path, mode='w') as file:
            json.dump(new_data, file, indent=4)
        return

    def add_purchase(self, purchase: Purchase, save: bool):
        self.purchases.append(purchase)
        self.save_to_file()
        return

    def edit_purchase(self, old_purchase: Purchase, new_purchase: Purchase) -> bool:
        try:
            self.purchases[self.purchases.index(old_purchase)] = new_purchase
            self.save_to_file()
        except ValueError:
            return False
        return True

    def delete_purchase(self, purchase: Purchase) -> bool:
        try:
            self.purchases.remove(purchase)
            self.save_to_file()
        except ValueError:
            return False
        return True

    def find_purchase(self, purchase_id: int|None = None, name: str|None = None, purchase_date: dt.date|None = None, category: str|None = None, brand: str|None = None, price: float|None = None, notes: str|None = None, tags: str|None = None):
        if name:
            name = name.lower()
        if category:
            category = category.lower()
        if brand:
            brand = brand.lower()
        if price is not None:
            try:
                price = float(price)
            except ValueError:
                price = None
                print("Price is in the wrong format, skipping search filter.")

        results = []

        for purchase in self.purchases:
            if (
                (purchase_id is None or purchase_id in purchase.id)
                and (name is None or name in purchase.name.lower())
                and (purchase_date is None or purchase.purchase_date == purchase_date)
                and (category is None or (purchase.category is not None and category in purchase.category.lower()))
                and (brand is None or (purchase.brand is not None and brand in purchase.brand.lower()))
                and (price is None or purchase.price == price)
                and matches_notes(purchase, notes)
                and matches_tags(purchase, tags)
            ):
                results.append(purchase)

        return results

    def print_purchases(self):
        # TODO: Custom columns?
        print(f"{'Name':<25} {'Brand':<15} {'Price':<10} {'Date':<12}")
        print("-" * 65)

        for purchase in self.purchases:
            brand = purchase.brand or "-"
            price_display = f"${purchase.price:.2f}" if purchase.price is not None else "-"
            date = str(purchase.purchase_date)

            print(f"{purchase.name:<25} {brand:<15} {price_display:<10} {date:<12}")
        return

class Purchase:
    def __init__(self, id: int, name: str, purchase_date: dt.date, category: str|None = None, brand: str|None = None, price: float|None = None, tags: list[str]|None = None, notes: list[dict]|None = None, files: list[dict]|None = None):
        self.id = id
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.purchase_date = purchase_date
        self.tags = tags
        self.notes = notes
        self.files = files

    def _to_dict(self):
        purchase = {
            "id": self.id,
            "name": self.name,
            "purchase_date": self.purchase_date.strftime("%d-%m-%Y"),
            "brand": self.brand,
            "category": self.category,
            "tags": self.tags,
            "price": self.price,
            "notes": self.notes,
            "files": self.files
        }
        return purchase

def matches_notes(purchase: Purchase, search_text: str|None) -> bool:
    if search_text is None:
        return True

    for note in (purchase.notes or []):
        if search_text.lower() in note.get("text", "").lower():
            return True
    return False

def matches_tags(purchase: Purchase, search_text: str|None) -> bool:
    if search_text is None:
        return True

    for tag in (purchase.tags or []):
        if search_text.lower() in tag.lower():
            return True
    return False

def ask_for_input(message: str, input_type: InputType, optional: bool, also_except: list[str] = []):
    """Prompts the user for input with a given message. Handles validation based on the choosen input type, and enforces input unless optional."""
    while True:
        user_input = input(message)

        if optional and user_input == "":
            return None

        if user_input in also_except:
            return user_input

        match input_type:
            case InputType.STRING:
                if user_input:
                    return user_input
                else:
                    print("** Invalid input: an input is required. **")
            case InputType.INTEGER:
                try:
                    input_check = int(user_input)
                except ValueError:
                    print("** Invalid input: enter a valid integer. **")
                    continue
                return input_check
            case InputType.FLOAT:
                try:
                    input_check = float(user_input)
                except ValueError:
                    print("** Invalid input: enter a valid floating point number. **")
                    continue
                return input_check
            case InputType.DATE:
                try:
                    input_check = dt.date.strptime(user_input, "%d-%m-%Y")
                except ValueError:
                    print("** Invalid input: enter a valid date (DD-MM-YYYY). **")
                    continue
                return input_check
            case InputType.FILE_PATH:
                if os.path.isfile(user_input):
                    return user_input
                else:
                    print("** Invalid input: choosen file path does not exist. **")
                    continue
            case InputType.FILE_PATH_NOT_EXIST:
                # TODO: Test if could be valid path?
                return user_input
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
    tag = ask_for_input("Please enter the product's tag (or leave empty) to search for (if required): ", InputType.STRING, True)
    note = ask_for_input("Please enter the product's note (or leave empty) to search for (if required): ", InputType.STRING, True)
    purchase_id = ask_for_input("Please enter the product's id (or leave empty) to search for (if required): ", InputType.INTEGER, True)

    purchases = archive.find_purchase(purchase_id=purchase_id, name=name, purchase_date=date, brand=brand, category=category, price=price, notes=note, tags=tag) # type: ignore
    return purchases

def prompt_and_edit_purchase(archive: PurchaseArchive,current_purchase: Purchase) -> bool:
    """Prompts the user to edit each field of data in a purchase, edits the purchase, and returns the success value."""

    print("For (most) inputs below, you can type %clear% to clear the original.")
    new_name = ask_for_input("Please enter the product name (if you want to edit it): ", InputType.STRING, True) or current_purchase.name

    new_date = ask_for_input("Please enter the purchase date (DD-MM-YYYY) (if you want to edit it): ", InputType.DATE, True, ["%clear"]) or current_purchase.purchase_date
    if new_date is "%clear": new_date = ""

    new_brand = ask_for_input("Please enter the product's brand (or leave empty) (if you want to edit it): ", InputType.STRING, True, ["%clear"]) or current_purchase.brand
    if new_brand is "%clear": new_brand = ""

    new_category = ask_for_input("Please enter the product's category (or leave empty) (if you want to edit it): ", InputType.STRING, True, ["%clear"]) or current_purchase.category
    if new_category is "%clear": new_category = ""

    new_price = ask_for_input("Please enter the product's price (or leave empty) (if you want to edit it): ", InputType.FLOAT, True, ["%clear"])
    if new_price is None:
        new_price = current_purchase.price

    # TODO: Edit tags, notes, files

    return archive.edit_purchase(current_purchase, Purchase(id=current_purchase.id, name=new_name, purchase_date=new_date, brand=new_brand, category=new_category, price=new_price, notes=current_purchase.notes, tags=current_purchase.tags, files=current_purchase.files)) # type: ignore

def display_home_menu():
    while True:
        print("-----Personal Purchase Archive -----\n")

        ARCHIVE.print_purchases()

        print("\n1. Add a new purchase")
        print("2. Edit an existing purchase")
        print("3. Delete an existing purchase")
        print("4. Load a different archive")
        print("5. Open purchase information")
        print("6. Create a new archive")
        print("7. Settings")
        print("8. Exit")

        user_input = ask_for_input("Enter your selection: ", InputType.INTEGER, False)

        if user_input == 8:
            break

        manage_home_input(user_input)

def choose_purchase(purchases: list[Purchase]) -> Purchase|Literal[False]:
    print("Multiple purchases found, please review below.\n")

    num_of_pages = math.ceil(len(purchases) / 10)
    page_num = 1

    display_purchase_page(purchases[0:9], page_num, num_of_pages)

    while True:
        user_input = ask_for_input("\nType the corresponding number to select a purchase or change page, or anything else to cancel.", InputType.STRING, True)

        if user_input is None:
            return False

        if user_input is ">":
            if page_num < num_of_pages:
                page_num += 1
            min_purchase = ((page_num - 1) * 10)
            max_purchase = ((page_num * 10) - 1)

            if max_purchase > len(purchases):
                max_purchase = len(purchases)

            display_purchase_page(purchases[min_purchase:max_purchase], page_num, num_of_pages)
        elif user_input is "<":
            if not page_num <= 2:
                page_num -= 1
            min_purchase = ((page_num - 1) * 10)
            max_purchase = ((page_num * 10) - 1)

            if max_purchase > len(purchases):
                max_purchase = len(purchases)

            display_purchase_page(purchases[((page_num - 1) * 10):((page_num * 10) - 1)], page_num, num_of_pages)
        else:
            try:
                user_input = int(user_input) # type: ignore
                if user_input > 0 and user_input < len(purchases) + 1: # type: ignore
                    current_purchase = purchases[user_input - 1] # type: ignore
                else:
                    return False
            except ValueError:
                return False
            return current_purchase

def display_purchase_page(purchases: list[Purchase], current_page_num: int, total_pages: int):
    for index, purchase in enumerate(purchases, start=1):
            price_display = f"${purchase.price:.2f}" if purchase.price is not None else "-"
            print(f"{index}. {purchase.name:<25} {purchase.brand:<15} {price_display:<10} {purchase.purchase_date:<12}")

    print(f"\nPage {current_page_num}")
    if total_pages > current_page_num and current_page_num > 1: 
        print("\">\" to page up, \"<\" to page down")
    elif current_page_num == 1 and total_pages > current_page_num:
        print("\">\" to page up")
    elif total_pages == current_page_num and current_page_num > 1:
        print("\"<\" to page down")
    else:
        pass

    return
        

def confirm_purchase(purchase: Purchase, action: str) -> bool:
    print("Please confirm the purchase below.\n")
    price_display = f"${purchase.price:.2f}" if purchase.price is not None else "-"

    print(f"{purchase.name:<25} {purchase.brand:<15} {price_display:<10} {purchase.purchase_date:<12}")

    user_input = ask_for_input(f"\nType \"yes\" to confirm, or anything else to cancel {action}: ", InputType.STRING, True)

    return user_input == "yes"

def wait_before_continue():
    ask_for_input("\nPress enter to continue.", InputType.STRING, True)
    return

def load_purchase_information(purchase: Purchase):
    print("Work in progress!")
    # TODO: load purchase information
    return

def create_archive(file_path, archive_name):
    default_archive = {
        "metadata": {
            "archive_name": archive_name,
            "next_id": 1
        },
        "purchases": []
    }

    with open(f"{file_path}", "x") as file:
        json.dump(default_archive, file, indent=4)
    return

def manage_home_input(user_input):
    match str(user_input):
        case "1":
            # -- Add a new purchase --
            name = ask_for_input("Please enter the product name: ", InputType.STRING, False)
            date = ask_for_input("Please enter the purchase date (DD-MM-YYYY): ", InputType.DATE, False)
            brand = ask_for_input("Please enter the product's brand (or leave empty): ", InputType.STRING, True)
            category = ask_for_input("Please enter the product's category (or leave empty): ", InputType.STRING, True)
            price = ask_for_input("Please enter the product's price (or leave empty): ", InputType.FLOAT, True)

            purchase_id = ARCHIVE.get_next_id()
            ARCHIVE.add_purchase(Purchase(id=purchase_id, name=name, purchase_date=date, brand=brand, category=category, price=price), True) # type: ignore
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
            # -- Load a different archive --
            user_input = ask_for_input("Please enter the file path of the archive: ", InputType.FILE_PATH, False)
            ARCHIVE.set_file_path(str(user_input))
            ARCHIVE.load_purchases()
        case "5":
            # -- Open purchase information --
            purchases = search_and_select_purchase(archive=ARCHIVE)
            
            if len(purchases) == 0:
                print("No purchases found, please try again.")
            elif len(purchases) == 1:
                if confirm_purchase(purchases[0], "selecting"):
                    load_purchase_information(purchases[0])
                else:
                    print("Selecting canceled.")
            elif len(purchases) < 6:
                current_purchase = choose_purchase(purchases)
                if current_purchase:
                    if confirm_purchase(current_purchase, "selecting"):
                        load_purchase_information(current_purchase)
                    else:
                        print("Selecting canceled.")
            else:
                print("Too many purchases matched. Please try again with a stricter match.")
        case "6":
            # -- Create a new archive --
            file_path = ask_for_input("Enter a file path to create a new archive: ", InputType.STRING, False)
            archive_name = ask_for_input("Enter a name for the archive: ", InputType.STRING, False)

            create_archive(file_path, archive_name)

        case "7":
            # -- Settings --
            print("\n1. Change default file path")
            print("2. View version information")
            print("3. Return")

            user_input = ask_for_input("Enter your selection: ", InputType.INTEGER, False)

            match str(user_input):
                case "1":
                    # Change default file path
                    user_input = ask_for_input("Please enter the new default file path: ", InputType.FILE_PATH, False)

                    with open("settings.json", "r") as file:
                        data = json.load(file)

                    data["default_file_path"] = user_input

                    with open("settings.json", "w") as file:
                        json.dump(data, file, indent=4)
                case "2":
                    # View version information
                    print("\nPersonal Purchase Archive (prerelease) by BingleyPro")
                    wait_before_continue()
        case "8":
            # Exit
            sys.exit()
        case _:
            print("** Invalid input, try again.**")

# -------------
ARCHIVE = PurchaseArchive()

if os.path.isfile("settings.json"):
    # Check settings.json for default file. If exists, load it. Otherwise, prompt user for archive.
    with open("settings.json", "r") as file:
        data = json.load(file)
        file_path = data["default_file_path"]

        if os.path.isfile(file_path):
            ARCHIVE.set_file_path(file_path)
            ARCHIVE.load_purchases()
        else:
            user_input = ask_for_input("Please enter the file path of the archive to open (will be created if it doesn't exist): ", InputType.FILE_PATH_NOT_EXIST, False)
            if not os.path.isfile(str(user_input)):
                file_path = ask_for_input("Enter a file path to create a new archive: ", InputType.STRING, False)
                archive_name = ask_for_input("Enter a name for the archive: ", InputType.STRING, False)
    
                create_archive(file_path, archive_name)

            ARCHIVE.set_file_path(str(user_input))
            ARCHIVE.load_purchases()
else:
    # Create settings.json
    user_input = ask_for_input("Please enter the file path of the archive to open (will open by default, will be created if it doesn't exist): ", InputType.FILE_PATH_NOT_EXIST, False)

    if not os.path.isfile(str(user_input)):
        file_path = ask_for_input("Enter a file path to create a new archive: ", InputType.STRING, False)
        archive_name = ask_for_input("Enter a name for the archive: ", InputType.STRING, False)

        create_archive(file_path, archive_name)

    ARCHIVE.set_file_path(str(user_input))
    ARCHIVE.load_purchases()

    with open("settings.json", "x") as file:
        data = {
            "default_file_path": user_input
         }
        json.dump(data, file)

display_home_menu()