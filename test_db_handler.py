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
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                current_amount INTEGER NOT NULL,
                price REAL NOT NULL
            )
        ''')
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

    def test_create_product(self):
        self.db_handler.create_product('Energy Drink', 50, 2.5)
        self.db_handler.cursor.execute('SELECT * FROM products WHERE name = "Energy Drink"')
        product = self.db_handler.cursor.fetchone()
        self.assertIsNotNone(product)
        self.assertEqual(product[1], 'Energy Drink')
        self.assertEqual(product[2], 50)
        self.assertEqual(product[3], 2.5)

    def test_add_product_storage(self):
        self.db_handler.create_product('Energy Drink', 50, 2.5)
        self.db_handler.add_product_storage(1, 20)
        self.db_handler.cursor.execute('SELECT current_amount FROM products WHERE id = 1')
        current_amount = self.db_handler.cursor.fetchone()[0]
        self.assertEqual(current_amount, 70)

    def test_buy_energy(self):
        self.db_handler.create_user(1, 'Alice', 100.0)
        self.db_handler.create_product('Energy Drink', 50, 2.5)
        self.db_handler.buy_energy(1, 1, 4)
        self.db_handler.cursor.execute('SELECT current_amount FROM products WHERE id = 1')
        current_amount = self.db_handler.cursor.fetchone()[0]
        self.assertEqual(current_amount, 46)
        self.db_handler.cursor.execute('SELECT money_amount FROM users WHERE id = 1')
        money_amount = self.db_handler.cursor.fetchone()[0]
        self.assertEqual(money_amount, 90.0)
        self.db_handler.cursor.execute('SELECT * FROM purchase_history WHERE user_id = 1 AND product_id = 1')
        purchase = self.db_handler.cursor.fetchone()
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase[3], 4)

if __name__ == '__main__':
    unittest.main()