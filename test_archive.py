import json
import datetime as dt

from app import PurchaseArchive, Purchase

def test_add_purchase(tmp_path):
    path = tmp_path / "test_archive.json"

    with open(path, 'w') as file:
        json.dump(
            {
                "metadata": {
                    "archive_name": "Test Archive",
                    "next_id": 1
                },
                "backup_file_path": "",
                "purchases": []
            }, file)

    archive = PurchaseArchive()
    archive.set_file_path(path)

    assert archive.load_purchases() is True

    purchase = Purchase(
        id = archive.get_next_id(),
        name = "Keyboard",
        purchase_date = dt.date(2026, 10, 1),
        brand = "Keychron",
        category = "Computer",
        price = 394.99,
        tags = ["keyboard", "accessory"]
    )

    assert archive.add_purchase(purchase) is True
    assert len(archive.purchases) == 1

    with open(path, 'r') as file:
        saved_data = json.load(file)

        assert len(saved_data["purchases"]) == 1
        assert saved_data["purchases"][0]["name"] == "Keyboard"
        assert saved_data["purchases"][0]["price"] == 394.99
        assert saved_data["metadata"]["next_id"] == 2