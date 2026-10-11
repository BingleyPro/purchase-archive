# Personal Purchase Archive

Personal Purchase Archive is a local application for recording purchases and useful information together. You can store a product's name, brand, price, purchase date and category, and revisit the entry in future to view notes, tags, and attached files, such as receipts, photographs or warranty information.

> Currently an active work in progress! **This project is only recommended for alpha use at this stage. Note that you shouldn't store sensitive information with this program currently without encryption.**

This project currently uses a terminal based interface, along with JSON for storing an archive. You can see an example structure of JSON in **dev_data/database.json**.

## Features

- Add, edit, search for and delete purchases.
- Search by name, purchase ID, purchase date, brand, category, price, tags or note text.
- View purchases using a paginated interface
- Create and switch between JSON archives
- Add, edit and delete notes assoicated with a purchase
- Create and edit purchase tags
- Attach, edit, and remove files
- View purchase details, inluding notes and attachments

### Missing features

- A graphical interface.
- Encryption.
- Automatic backups.
- Drag-and-drop attachment uploading
- Purchase sorting.
- Most user settings.

## Running (from source)

To build and run from source, clone the repository. Then create a virtual environment in the root directory:
`python3 -m venv .venv`

Activate it:
`source .venv/bin/activate`

Finally, install the dependencies and launch:
`python3 -m pip install -r requirements.txt`
`python3 app.py`

## Running (from packaged release)

Download the builds from the releases on the side. For Windows, run the `.exe` fle. For Mac, extract the archive and run `./PersonalPurchaseArchive`.

Note that these are unsigned alpha builds.
