import unittest
import sqlite3
from db_handler import DBHandler

class TestDBHandler(unittest.TestCase):
    def setUp(self):
        self.db_handler = DBHandler(':memory:')  # Use in-memory database for testing
        self.db_handler.cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                money_amount REAL NOT NULL
            )
        ''')
        self.db_handler.cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                current_amount INTEGER NOT NULL,
                price REAL NOT NULL,
                image_filename TEXT DEFAULT 'default.png'
            )
        ''')
        # It's good practice to also create other tables if they are interacted with,
        # even indirectly by methods being tested, or if foreign key constraints are involved.
        # The purchase_history table has foreign keys to products and users.
        self.db_handler.cursor.execute('''
            CREATE TABLE purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.db_handler.conn.commit()

    def tearDown(self):
        self.db_handler.close()

    def test_create_user(self):
        self.db_handler.create_user(1, 'Alice', 100.0)
        self.db_handler.cursor.execute('SELECT * FROM users WHERE id = 1')
        user = self.db_handler.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], 'Alice')
        self.assertEqual(user[2], 100.0)

    def test_create_product_with_image(self):
        # This test now checks for image_filename
        self.db_handler.create_product('Energy Drink', 50, 2.5, 'energy.png')
        # Fetch product by name to get its ID for further checks if needed
        self.db_handler.cursor.execute('SELECT id, name, current_amount, price, image_filename FROM products WHERE name = "Energy Drink"')
        product = self.db_handler.cursor.fetchone()
        self.assertIsNotNone(product)
        self.assertEqual(product[1], 'Energy Drink') # name
        self.assertEqual(product[2], 50) # current_amount
        self.assertEqual(product[3], 2.5) # price
        self.assertEqual(product[4], 'energy.png') # image_filename
        
        # Test default image filename
        self.db_handler.create_product('Water', 100, 1.0, 'default.png') # Explicitly default
        self.db_handler.cursor.execute('SELECT image_filename FROM products WHERE name = "Water"')
        product_water = self.db_handler.cursor.fetchone()
        self.assertEqual(product_water[0], 'default.png')


    def test_add_product_storage(self):
        # Products need image_filename now
        self.db_handler.create_product('Energy Drink', 50, 2.5, 'energy.png')
        # Assuming create_product returns id or we fetch it.
        # For simplicity, assuming product created has ID 1 if it's the first.
        # Better: fetch id after creation if not returned.
        self.db_handler.cursor.execute('SELECT id FROM products WHERE name = "Energy Drink"')
        product_id = self.db_handler.cursor.fetchone()[0]
        
        self.db_handler.add_product_storage(product_id, 20)
        self.db_handler.cursor.execute('SELECT current_amount FROM products WHERE id = ?', (product_id,))
        current_amount = self.db_handler.cursor.fetchone()[0]
        self.assertEqual(current_amount, 70)

    def test_buy_energy_by_id(self): # Renamed test to match method, if applicable
        self.db_handler.create_user(1, 'Alice', 100.0)
        # Products need image_filename
        self.db_handler.create_product('Energy Drink', 50, 2.5, 'energy.png')
        self.db_handler.cursor.execute('SELECT id FROM products WHERE name = "Energy Drink"')
        product_id = self.db_handler.cursor.fetchone()[0]

        self.db_handler.buy_energy_by_id(1, product_id, 4) # Assuming buy_energy_by_id is the correct method
        
        self.db_handler.cursor.execute('SELECT current_amount FROM products WHERE id = ?', (product_id,))
        current_amount = self.db_handler.cursor.fetchone()[0]
        self.assertEqual(current_amount, 46)
        
        self.db_handler.cursor.execute('SELECT money_amount FROM users WHERE id = 1')
        money_amount = self.db_handler.cursor.fetchone()[0]
        self.assertEqual(money_amount, 90.0)
        
        self.db_handler.cursor.execute('SELECT * FROM purchase_history WHERE user_id = 1 AND product_id = ?', (product_id,))
        purchase = self.db_handler.cursor.fetchone()
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase[3], 4) # amount in purchase_history

    def test_get_product_details(self):
        self.db_handler.create_product('Test Soda', 30, 1.5, 'soda.jpg')
        self.db_handler.cursor.execute('SELECT id FROM products WHERE name = "Test Soda"')
        product_id = self.db_handler.cursor.fetchone()[0]

        details = self.db_handler.get_product_details(product_id)
        self.assertIsNotNone(details)
        self.assertEqual(details['id'], product_id)
        self.assertEqual(details['name'], 'Test Soda')
        self.assertEqual(details['current_amount'], 30)
        self.assertEqual(details['price'], 1.5)
        self.assertEqual(details['image_filename'], 'soda.jpg')

        self.assertIsNone(self.db_handler.get_product_details(999)) # Test non-existent product

    def test_get_all_products_with_details(self):
        self.db_handler.create_product('Juice', 20, 3.0, 'juice.png')
        self.db_handler.create_product('Coffee', 40, 2.0, 'coffee.bmp')
        
        products = self.db_handler.get_all_products_with_details()
        self.assertEqual(len(products), 2)
        
        # Verify details of one product (e.g., Juice)
        juice_details = next((p for p in products if p['name'] == 'Juice'), None)
        self.assertIsNotNone(juice_details)
        self.assertEqual(juice_details['current_amount'], 20)
        self.assertEqual(juice_details['price'], 3.0)
        self.assertEqual(juice_details['image_filename'], 'juice.png')

    def test_update_product_stock(self):
        self.db_handler.create_product('Tea', 15, 1.0, 'tea.gif')
        self.db_handler.cursor.execute('SELECT id FROM products WHERE name = "Tea"')
        product_id = self.db_handler.cursor.fetchone()[0]

        self.db_handler.update_product_stock(product_id, 25)
        details = self.db_handler.get_product_details(product_id)
        self.assertEqual(details['current_amount'], 25)

    def test_delete_product(self):
        self.db_handler.create_product('Water', 100, 0.5, 'water.png')
        self.db_handler.cursor.execute('SELECT id FROM products WHERE name = "Water"')
        product_id = self.db_handler.cursor.fetchone()[0]

        self.db_handler.delete_product(product_id)
        self.assertIsNone(self.db_handler.get_product_details(product_id))
        
        # Ensure it's actually gone from the table
        self.db_handler.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = self.db_handler.cursor.fetchone()
        self.assertIsNone(product)

if __name__ == '__main__':
    unittest.main()