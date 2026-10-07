"""
Personal Purchase Archive

Author: BingleyPro
Copyright: 2026
"""

from flask import Flask, render_template, request
import datetime as dt
import csv

app = Flask(__name__)

class PurchaseArchive:
    def __init__(self):
        self.purchases = []

    def add_purchase(self, purchase: Purchase) -> bool:
        self.purchases.append(purchase)
        return True

    def edit_purchase(self, old_purchase: Purchase, new_purchase: Purchase) -> bool:
        try:
            self.purchases[self.purchases.index(old_purchase)] = new_purchase
        except:
            return False
        return True

    def delete_purchase(self, purchase: Purchase) -> bool:
        try:
            self.purchases.remove(purchase)
        except:
            return False
        return True

    def find_purchase(self, name: str|None = None, purchase_date: dt.date|None = None, category: str|None = None, brand: str|None = None, price: float|None = None, notes: list[str]|None = None):

        # Less strict matching
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
                print("Price is in the wrong format, skipping search.")
        if notes:
            # Notes is an array of strings
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

            print(f"{purchase.name:<25} {brand:<15} ${price:<10} {purchase.purchase_date:<12}")

class Purchase:
    def __init__(self, name: str, purchase_date: dt.date, category: str|None = None, brand: str|None = None, price: float|None = None, notes: list[str]|None = None):
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.purchase_date = purchase_date
        self.notes = notes

def print_choices():
    print("\n1. Add a new purchase")
    print("2. Edit an existing purchase")
    print("3. Delete an existing purchase")
    print("4. Load a different archive")
    print("5. Settings")

def prompt_user():
    archive.print_purchases()
    print_choices()
    user_input = input("Enter your selection: ")
    manage_input(user_input)

def manage_input(user_input):
    match str(user_input):
        case "1":
            # Add a new purchase
            name = input("Please enter the product name: ")
            date = dt.datetime.strptime(input("Please enter the purchase date (DD-MM-YYYY): "), "%d-%m-%Y").date()
            brand = input("Please enter the product's brand (or leave empty): ") or None
            category = input("Please enter the product's category (or leave empty): ") or None
            price_input = input("Please enter the product's price (or leave empty): ")

            if price_input:
                price = float(price_input)
            else:
                price = None

            archive.add_purchase(Purchase(name=name, purchase_date=date, brand=brand, category=category, price=price))
        case "2":
            # Edit an existing purchase
            name = input("Please enter the product name to search for (if required): ") or None
            date = dt.datetime.strptime(input("Please enter the purchase date (DD-MM-YYYY) to search for (if required): "), "%d-%m-%Y").date()
            brand = input("Please enter the product's brand (or leave empty) to search for (if required): ") or None
            category = input("Please enter the product's category (or leave empty) to search for (if required): ") or None
            price_input = input("Please enter the product's price (or leave empty) to search for (if required): ")

            if price_input:
                price = float(price_input)
            else:
                price = None

            purchases = archive.find_purchase(name=name, purchase_date=date, brand=brand, category=category, price=price)
            if len(purchases) == 0:
                print("No purchases found, please try again.")
            elif len(purchases) == 1:
                print("Purchase found, please confirm below.\n")
                print(f"{purchases[0].name:<25} {brand:<15} ${price:<10} {purchases[0].purchase_date:<12}")
                
                current_purchase = purchases[0]

                user_input = input("\nType \"yes\" to confirm, or anything else to cancel editing: ")

                if user_input == "yes":
                    new_name = input("Please enter the product name (if you want to edit it): ") or current_purchase.name
                    new_date = dt.datetime.strptime(input("Please enter the purchase date (DD-MM-YYYY) (if you want to edit it): "), "%d-%m-%Y").date() or current_purchase.date
                    new_brand = input("Please enter the product's brand (or leave empty) (if you want to edit it): ") or current_purchase.brand
                    new_category = input("Please enter the product's category (or leave empty) (if you want to edit it): ") or current_purchase.category
                    price_input = input("Please enter the product's price (or leave empty) (if you want to edit it): ")

                    if price_input:
                        new_price = float(price_input)
                    else:
                        new_price = current_purchase.price

                    archive.edit_purchase(current_purchase, Purchase(name=new_name, purchase_date=new_date, brand=new_brand, category=new_category, price=new_price, notes=current_purchase.notes))
                    print("Purchase edited.")
                else:
                    print("Editing canceled.")
            elif len(purchases) < 6:
                print("Multiple purchases found, please review below.\n")
                index = 1
                for purchase in purchases:
                    print(f"{purchase.name:<25} {brand:<15} ${price:<10} {purchase.purchase_date:<12}")
                    index += 1
                user_input = input("\nType the corresponding number to select a purchase, or anything else to cancel.")

                if int(user_input) > 0 and int(user_input) < len(purchases) + 1:
                    current_purchase = purchases[int(user_input) - 1]
                else:
                    print("Editing canceled.")
                    return

                print(f"{current_purchase.name:<25} {brand:<15} ${price:<10} {current_purchase.purchase_date:<12}")

                user_input = input("\nType \"yes\" to confirm, or anything else to cancel editing: ")

                if user_input == "yes":
                    new_name = input("Please enter the product name (if you want to edit it): ") or current_purchase.name
                    new_date = dt.datetime.strptime(input("Please enter the purchase date (DD-MM-YYYY) (if you want to edit it): "), "%d-%m-%Y").date() or current_purchase.date
                    new_brand = input("Please enter the product's brand (or leave empty) (if you want to edit it): ") or current_purchase.brand
                    new_category = input("Please enter the product's category (or leave empty) (if you want to edit it): ") or current_purchase.category
                    price_input = input("Please enter the product's price (or leave empty) (if you want to edit it): ")

                    if price_input:
                        new_price = float(price_input)
                    else:
                        new_price = current_purchase.price

                    archive.edit_purchase(current_purchase, Purchase(name=new_name, purchase_date=new_date, brand=new_brand, category=new_category, price=new_price, notes=current_purchase.notes))
                    print("Purchase edited.")
                else:
                    print("Editing canceled.")
                    return
            else:
                print("Too many purchases matched. Please try again with a stricter match.")
            
            pass
        case "3":
            # Delete an existing purchase
            name = input("Please enter the product name to search for (if required): ") or None
            date = dt.datetime.strptime(input("Please enter the purchase date (DD-MM-YYYY) to search for (if required): "), "%d-%m-%Y").date()
            brand = input("Please enter the product's brand (or leave empty) to search for (if required): ") or None
            category = input("Please enter the product's category (or leave empty) to search for (if required): ") or None
            price_input = input("Please enter the product's price (or leave empty) to search for (if required): ")

            if price_input:
                price = float(price_input)
            else:
                price = None

            purchases = archive.find_purchase(name=name, purchase_date=date, brand=brand, category=category, price=price)
        case "4":
            # Load a different archive
            print("Coming soon!")
            pass
        case "5":
            # Settings
            print("There are currently no settings!")
            pass
        case _:
            archive.print_purchases()
            print_choices()
            user_input = input("Invalid input, try again: ")
            manage_input(user_input)
    prompt_user()
            
# Examples
purchases = [
    Purchase("Electric Screwdriver", dt.date(2026, 10, 5), "Tool", price = 90.95),
    Purchase("Keyboard", dt.date(2026, 10, 1), "Computer", "Keychron", 210.00),
    Purchase("A1 Mini", dt.date(2026, 9, 20), "3D Printer", "Bambu Lab", 394.99)
]

archive = PurchaseArchive()
archive.add_purchase(purchases[0])
archive.add_purchase(purchases[1]) 
archive.add_purchase(purchases[2])

# Functionality
print("-----Personal Purchase Archive -----\n")

archive.print_purchases()
print_choices()
user_input = input("Enter your selection: ")
manage_input(user_input)



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