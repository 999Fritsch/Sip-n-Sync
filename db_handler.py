import sqlite3

class DBHandler:
    def __init__(self, db_name='energy_drinks.db'):
        """
        Initializes the database handler and establishes a connection to the specified database.

        Args:
            db_name (str): The name of the database file to connect to. Defaults to 'energy_drinks.db'.
        """
        self.connect(db_name)
        self.map_flavor_to_id()

    def fetch_products(self):
        """Fetches product id and name from the database."""
        self.cursor.execute('SELECT id, name FROM products')
        products = self.cursor.fetchall()
        # Return a list of dictionaries for easier template usage.
        return [{'id': p[0], 'name': p[1]} for p in products]

    def get_product_details(self, product_id):
        """
        Fetches id, name, current_amount, price, and image_filename for a given product_id.

        Args:
            product_id (int): The ID of the product to fetch.

        Returns:
            dict: A dictionary containing product details, or None if not found.
        """
        self.cursor.execute('SELECT id, name, current_amount, price, image_filename FROM products WHERE id = ?', (product_id,))
        product = self.cursor.fetchone()
        if product:
            return {'id': product[0], 'name': product[1], 'current_amount': product[2], 'price': product[3], 'image_filename': product[4]}
        return None

    def get_all_products_with_details(self):
        """
        Fetches id, name, current_amount, price, and image_filename for all products.

        Returns:
            list: A list of dictionaries, each containing product details.
        """
        self.cursor.execute('SELECT id, name, current_amount, price, image_filename FROM products')
        products = self.cursor.fetchall()
        return [{'id': p[0], 'name': p[1], 'current_amount': p[2], 'price': p[3], 'image_filename': p[4]} for p in products]

    def update_product_stock(self, product_id, new_stock):
        """
        Updates the current_amount of a product to new_stock.

        Args:
            product_id (int): The ID of the product to update.
            new_stock (int): The new stock amount.

        Returns:
            None
        """
        self.cursor.execute('UPDATE products SET current_amount = ? WHERE id = ?', (new_stock, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        """
        Deletes a product from the products table based on product_id.

        Args:
            product_id (int): The ID of the product to delete.

        Returns:
            None
        """
        self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        self.conn.commit()

    def create_user(self, user_id, name, money_amount):
        """
        Creates a new user in the database.

        Args:
            user_id (int): The unique identifier for the user.
            name (str): The name of the user.
            money_amount (float): The initial amount of money for the user.

        Returns:
            None
        """
        self.cursor.execute('INSERT OR IGNORE INTO users (id, name, money_amount) VALUES (?, ?, ?)', (user_id, name, money_amount))
        self.conn.commit()

    def create_product(self, name, current_amount, price, image_filename):
        """
        Inserts a new product into the products table.

        Args:
            name (str): The name of the product.
            current_amount (int): The current amount of the product in stock.
            price (float): The price of the product.
            image_filename (str): The filename of the product image.

        Returns:
            None
        """
        self.cursor.execute('INSERT INTO products (name, current_amount, price, image_filename) VALUES (?, ?, ?, ?)', (name, current_amount, price, image_filename))
        self.conn.commit()

    def add_product_storage(self, product_id, amount):
        """
        Adds the specified amount to the current storage of the product.

        Args:
            product_id (int): The ID of the product to update.
            amount (int): The amount to add to the current storage.

        Returns:
            None
        """
        self.cursor.execute('UPDATE products SET current_amount = current_amount + ? WHERE id = ?', (amount, product_id))
        self.conn.commit()
    
    def add_money_to_user(self, user_id, amount):
        """
        Adds the specified amount of money to the user's account.

        Args:
            user_id (int): The ID of the user to update.
            amount (float): The amount of money to add to the user's account.

        Returns:
            None
        """
        self.cursor.execute('UPDATE users SET money_amount = money_amount + ? WHERE id = ?', (amount, user_id))
        self.conn.commit()

    def buy_energy_by_id(self, user_id, product_id, amount):
        """
        Processes the purchase of energy by a user.

        Args:
            user_id (int): The ID of the user making the purchase.
            product_id (int): The ID of the product being purchased.
            amount (int): The amount of the product to purchase.

        Raises:
            ValueError: If the product is not found.
            ValueError: If there is not enough product in stock.
            ValueError: If the user is not found.

        Performs the following steps:
            1. Retrieves product information from the database.
            2. Checks if there is enough product in stock.
            3. Retrieves user information from the database.
            4. Updates the product stock and user's money amount.
            5. Inserts a record into the purchase history.
            6. Commits the transaction to the database.
        """
        # Produktinformationen abrufen
        self.cursor.execute('SELECT current_amount, price FROM products WHERE id = ?', (product_id,))
        product = self.cursor.fetchone()
        if product is None:
            raise ValueError("Produkt nicht gefunden")

        current_amount, price = product
        # removed this line to allow negative stock
        #if current_amount < amount:
        #    raise ValueError("Nicht genügend Produkt auf Lager")

        # Benutzerinformationen abrufen
        self.cursor.execute('SELECT money_amount FROM users WHERE id = ?', (user_id,))
        user = self.cursor.fetchone()
        if user is None:
            raise ValueError("Benutzer nicht gefunden")

        money_amount = user[0]
        total_cost = price * amount

        # Kauf durchführen
        self.cursor.execute('UPDATE products SET current_amount = current_amount - ? WHERE id = ?', (amount, product_id))
        self.cursor.execute('UPDATE users SET money_amount = money_amount - ? WHERE id = ?', (total_cost, user_id))
        self.cursor.execute('INSERT INTO purchase_history (product_id, user_id, amount) VALUES (?, ?, ?)', (product_id, user_id, amount))

        self.conn.commit()

    def buy_energy_by_flavor(self, user_id, flavor_name, amount):
        """
        Purchase energy of a specific flavor for a user.

        Args:
            user_id (int): The ID of the user making the purchase.
            flavor_name (str): The name of the flavor to purchase.
            amount (int): The amount of energy to purchase.

        Raises:
            KeyError: If the flavor_name is not found in the flavor mapping.
        """
        self.flavors = self.map_flavor_to_id()
        self.buy_energy_by_id(user_id, self.flavors[flavor_name], amount)

    def map_flavor_to_id(self):
        """
        Maps product flavors to their corresponding IDs.

        Returns:
            dict: A dictionary with product flavors as keys and product IDs as values.
        """
        self.cursor.execute('SELECT id, name FROM products')
        products = self.cursor.fetchall()
        flavor_to_id = {name: product_id for product_id, name in products}
        self.flavors = flavor_to_id
        return flavor_to_id
    
    def check_user_id(self, user_id):
        """
        Checks if a user ID exists in the users table.

        Args:
            user_id (int): The ID of the user to check.

        Returns:
            bool: True if the user ID exists, False otherwise.
        """
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] > 0
      
    def close(self):
        """
        Closes the database connection.

        This method closes the connection to the database that was opened
        when the instance of the class was created. It is important to call
        this method to free up database resources.
        """
        self.conn.close()

    def connect(self, db_name='energy_drinks.db'):
        """
        Establishes a connection to the specified SQLite database and creates a cursor object.

        Args:
            db_name (str): The name of the database file to connect to. Defaults to 'energy_drinks.db'.

        Attributes:
            conn (sqlite3.Connection): The connection object to the SQLite database.
            cursor (sqlite3.Cursor): The cursor object for executing SQL commands.
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()