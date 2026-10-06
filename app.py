"""
Personal Purchase Archive

Author: BingleyPro
Copyright: 2026
"""

from flask import Flask, render_template, request
import datetime as dt


app = Flask(__name__)

class PurchaseArchive:
    def __init__(self):
        self.purchases = []

    def add_purchase(self, purchase):
        self.purchases.append(purchase)

    def delete_purchase(self, purchase):
        self.purchases.remove(purchase)

class Purchase:
    def __init__(self, name: str, purchase_date: dt.date, category: str|None = None, brand: str|None = None, price: float|None = None, notes = None):
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.purchase_date = purchase_date
        self.notes = notes

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

# Print table of purchases
print(f"{'Name':<25} {'Brand':<15} {'Price':<10} {'Date':<12}")
print("-" * 65)

for purchase in archive.purchases:
    brand = purchase.brand or "-"
    price = purchase.price if purchase.price is not None else "-"

    print(f"{purchase.name:<25} {brand:<15} ${price:<10} {purchase.purchase_date:<12}")



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