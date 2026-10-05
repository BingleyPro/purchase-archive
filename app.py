"""
Personal Purchase Archive

Author: BingleyPro
Copyright: 2026
"""

from flask import Flask, render_template, request
from markupsafe import escape

app = Flask(__name__)

class Purchase:
    def __init__(self, name, category, brand, price, purchase_date):
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.purchase_date = purchase_date

purchases = [
    Purchase("Electric Screwdriver", "Tool", "?", "90.95", "2026-10-05"),
    Purchase("Keyboard", "Computer", "Keychron", 210.00, "2026-10-01"),
    Purchase("A1 Mini", "3D Printer", "Bambu Lab", 394.99, "2026-09-20")  
]

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

if __name__ == "__main__":
    app.run()