# Personal Purchase Archive

This software solution is a tool for keeping track of purchases that you have made. You can then go back in future to review your past purchases and check any key information, like warranty details or serial numbers.

It will (coming soon!) be able store photos, serial numbers, receipts, and other information about products.

> Currently an active work in progress! **This project is only recommended for alpha use at this stage.**

This project currently uses a terminal based interface, along with JSON for storing an archive. You can see an example structure of JSON in **database.json**. Note that you shouldn't store sensitive information with this program currently without encryption.

## Features

- Add purchases
- Edit previous purchases
- Delete previous purchases
- Load custom archives

## Planned Features

- Upload or link files like PDFs (e.g receipts, photos of the product)

## Potential Features

- Drag-and-drop uploading
- Graphical interface (Flask or PyQt)
- Encyription?

## Usage Instructions

1. Initialise a virtual environment, and open it.
2. Install everything in requirements.txt
3. Run **app.py** using python3. Note that if the program asks for a file path, it is relative to the folder that app.py is located in.
4. Keep backups of your database JSON file!
