# Sip-n-Sync

Sip-n-Sync is a Flask-based web application that provides an easy-to-use interface for buying energy drinks from the office fridge. The application allows users to add products to their cart, remove them, and place orders. It also maintains a database of products, users, and purchase history.

## Features

- Display available products
- Add and remove products from the cart
- Place orders
- Maintain purchase history
- User authentication by user ID

## Project Structure

```
.gitignore
app.py
db_handler.py
init_db.py
README.md
requirements.txt
templates/
    order.html
test_db_handler.py
```

- `app.py`: Main application file that sets up the Flask app and routes.
- `db_handler.py`: Contains the `DBHandler` class for database operations.
- `init_db.py`: Script to initialize the SQLite database.
- `requirements.txt`: Lists the Python dependencies.
- `templates/order.html`: HTML template for the order page.
- `test_db_handler.py`: Unit tests for the `DBHandler` class.

## Getting Started

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/sip-n-sync.git
cd sip-n-sync
```

2. Install the required Python packages:

```sh
pip install -r requirements.txt
```

3. Initialize the database:

```sh
python init_db.py
```

### Running the Application

Start the Flask application:

```sh
python app.py
```

The application will be available at `http://127.0.0.1:5000/`.

### Running Tests

To run the unit tests, use the following command:

```sh
python -m unittest test_db_handler.py
```

## Usage

1. Open the application in your web browser.
2. Add products to your cart by clicking the "Hinzufügen" button.
3. Remove products from your cart by clicking the "Entfernen" button.
4. Enter your user ID and click "Bestellen" to place an order.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.