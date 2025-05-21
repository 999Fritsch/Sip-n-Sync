# Sip-n-Sync

**Project Description:**

Sip-n-Sync is a Flask-based web application designed for managing and purchasing energy drinks from an office fridge. It provides a user-friendly interface for users to browse products, add them to a cart, and place orders. The application also includes administrative features for managing products and user accounts. It maintains a database of products, users, purchase history, and transaction logs.

**Features:**

*   **Product Management:**
    *   Display available energy drinks with images, prices, and stock levels.
    *   Administrators can add new products, including their name, initial stock, and price.
    *   Administrators can refill the stock of existing products.
*   **User Account Management:**
    *   User authentication based on a unique user ID.
    *   Users can create new accounts with an initial balance.
    *   Users can add funds to their accounts.
    *   Session management with activity timeout.
*   **Ordering System:**
    *   Users can add and remove products from their shopping cart.
    *   Place orders from the items in the cart.
    *   User balance is updated automatically after a purchase.
    *   Product stock is updated automatically after a purchase.
*   **Transaction Tracking:**
    *   Maintains a history of all purchases.
    *   Logs various transaction types, including new users, new products, refills, and money additions.
    *   Users can view their personal transaction history.
*   **Deposit Management:**
    *   Administrators can add deposit amounts to a designated "Zugkasse" account (user ID 69).

## Project Structure

```
.
├── .gitignore             # Specifies intentionally untracked files that Git should ignore
├── README.md              # This file, providing an overview of the project
├── app.py                 # Main Flask application file with all routes and core logic
├── db_handler.py          # Contains the DBHandler class for database interactions (deprecated, logic moved to app.py)
├── init_db.py             # Script to initialize the SQLite database and create tables
├── migrate_db.py          # Script for database schema migrations (if any)
├── requirements.txt       # Lists the Python dependencies for the project
├── sync_products.py       # Script to synchronize product list with an external source or file (likely)
├── static/                # Directory for static files (CSS, JavaScript, images)
│   └── images/            # Contains images for the energy drinks
├── templates/             # Directory for HTML templates used by Flask
│   ├── add_money.html     # Template for users to add money to their account
│   ├── add_user.html      # Template for creating a new user account
│   ├── base.html          # Base template that other templates extend
│   ├── header.html        # Template for the header/navigation bar
│   ├── login.html         # Template for the user login page
│   ├── manage_products.html # Template for administrators to manage products (add, refill)
│   ├── navigation.html    # Template for site navigation links (likely part of header or base)
│   ├── order.html         # Template for displaying products and placing orders
│   └── transaction_history.html # Template for displaying user's transaction history
└── test_db_handler.py     # Unit tests for the database handler functionalities
```

-   `app.py`: Main application file that sets up the Flask app, routes, and includes the `DBHandler` class logic.
-   `db_handler.py`: This file originally contained the `DBHandler` class. Its database interaction logic has been integrated into `app.py`. It might be present for historical reasons or phased out.
-   `init_db.py`: Script to initialize the SQLite database (`energy_drinks.db`) and create the necessary tables (e.g., `products`, `users`, `purchase_history`, `transaction_history`).
-   `migrate_db.py`: Script used to apply changes or updates to the database schema after initial setup.
-   `requirements.txt`: Lists all Python packages required to run the project (e.g., Flask).
-   `sync_products.py`: A utility script likely used to update the product information in the database from an external source or predefined list.
-   `static/`: Contains static assets like product images.
    -   `images/`: Stores all the `.png` files for the different energy drink flavors.
-   `templates/`: Contains HTML files that are rendered by Flask to display information to the user.
    -   `base.html`: A base HTML structure inherited by other templates to maintain a consistent layout.
    -   `header.html`: Likely contains the HTML for the top part of the pages, including navigation.
    -   `login.html`: Page for user login.
    -   `order.html`: Page where users can see products and place orders.
    -   `add_money.html`: Page for users to add funds to their account.
    -   `add_user.html`: Page for new user registration.
    -   `manage_products.html`: Page for administrators to add new products or refill stock.
    -   `navigation.html`: Could be a part of `header.html` or a separate navigation component.
    -   `transaction_history.html`: Page for users to view their past transactions.
-   `test_db_handler.py`: Contains unit tests to verify the functionality of database operations.

## Getting Started

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd <repository-name>
    ```
    (Replace `<your-repository-url>` and `<repository-name>` with the actual URL and name)

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    This script creates the `energy_drinks.db` file and sets up the necessary tables.
    ```sh
    python init_db.py
    ```

## Database Migration

If there are updates to the database schema (e.g., new tables, modified columns), you will need to run the migration script. The `migrate_db.py` script is designed to apply these changes.

-   **When to run:** After pulling changes from the repository that include updates to database structure.
-   **How to run:**
    ```sh
    python migrate_db.py
    ```
    Ensure you have a backup of your database before running migration scripts, especially in a production environment.

## Running the Application

1.  **Ensure your virtual environment is activated** (if you created one):
    ```sh
    source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
    ```

2.  **Start the Flask application:**
    ```sh
    python app.py
    ```

    The application will typically be available at `http://127.0.0.1:5000/`. You will be redirected to the login page.

## Running Tests

To run the unit tests for the database handler functionalities:

```sh
python -m unittest test_db_handler.py
```

## Usage

1.  **Login/Register:**
    *   Access the application via `http://127.0.0.1:5000/`.
    *   If you are a new user, navigate to the "Add User" page (`/add_user`) to create an account with your User ID (must be at least 8 digits, unless it's the admin ID '69') and initial balance.
    *   Existing users can log in using their User ID.

2.  **Ordering Drinks (User):**
    *   Once logged in, you'll see the main products page (`/`).
    *   Browse available drinks.
    *   Click "Hinzufügen" (Add) to add a drink to your cart.
    *   Click "Entfernen" (Remove) to remove a drink from your cart.
    *   When ready, click "Bestellen" (Order) to purchase the items in your cart. Your balance will be updated.

3.  **Managing Funds (User):**
    *   Navigate to "Add Money" (`/add_money`) to add funds to your account.

4.  **Viewing History (User):**
    *   Go to "Transaction History" (`/transaction_history`) to see a list of your past purchases and deposits.

5.  **Product Management (Admin - User ID 69):**
    *   Log in with User ID `69`.
    *   Navigate to "Manage Products" (`/manage_products`).
    *   **Create New Product:** Fill in the name, initial amount, and price, then click "Create Product".
    *   **Refill Stock:** Select a product, enter the amount to add, and click "Refill".
    *   **Add Deposit:** Enter the deposit amount and click "Add Deposit to Zugkasse". This adds funds to the special User ID `69` account.

6.  **Logout:**
    *   Click on "Logout" in the navigation bar to end your session.

## Contributing

Contributions are welcome! If you have suggestions for improvements, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeatureName`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some YourFeatureName'`).
5.  Push to the branch (`git push origin feature/YourFeatureName`).
6.  Open a Pull Request.

Please ensure your code adheres to any existing style guidelines and includes tests where appropriate.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

*This README was generated with assistance from an AI coding partner.*
