import os
import unittest
import tempfile
import shutil
from flask import Flask
from app import app, db_handler # Assuming your Flask app instance is named 'app' and you can import db_handler
from db_handler import DBHandler # For direct DB manipulation if needed

class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a temporary folder for uploads
        self.upload_folder = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = self.upload_folder
        
        # Use a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        app.config['TESTING'] = True
        # Configure app to use the temporary DB. This depends on how db_handler is initialized in app.py
        # For this example, I'll assume db_handler can be re-initialized or its connection can be changed.
        # The simplest way is to ensure db_handler in app.py uses a configurable db_name.
        # If app.py's db_handler is a global, we might need to directly patch its db_name or reinitialize it.
        
        # Re-initialize db_handler for the test database
        # This is a critical part: Ensure the app's global db_handler uses the test DB
        self.original_db_handler_conn = db_handler.conn
        self.original_db_handler_cursor = db_handler.cursor
        
        # Create a new DBHandler instance for testing that points to the temporary DB
        self.test_db_handler = DBHandler(self.db_path)
        
        # Monkey patch the global db_handler in the app module to use the test_db_handler's connection
        # This is a common way to redirect database operations in tests.
        db_handler.conn = self.test_db_handler.conn
        db_handler.cursor = self.test_db_handler.cursor
        
        self.client = app.test_client()

        # Create tables in the temporary database
        with self.test_db_handler.conn: # Use the connection from our test_db_handler
            self.test_db_handler.cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    money_amount REAL NOT NULL
                )
            ''')
            self.test_db_handler.cursor.execute('''
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    current_amount INTEGER NOT NULL,
                    price REAL NOT NULL,
                    image_filename TEXT DEFAULT 'default.png'
                )
            ''')
            self.test_db_handler.cursor.execute('''
                CREATE TABLE purchase_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            self.test_db_handler.cursor.execute('''
                CREATE TABLE transaction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    transaction_type TEXT NOT NULL,
                    user_id INTEGER,
                    product_id INTEGER,
                    amount REAL,
                    description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
        
        # Create a dummy user for session if needed for login_required routes
        self.test_db_handler.create_user(12345678, "Test User", 100.0)


    def tearDown(self):
        # Restore original db_handler connection and cursor in app
        db_handler.conn = self.original_db_handler_conn
        db_handler.cursor = self.original_db_handler_cursor
        
        # Close the connection of test_db_handler
        self.test_db_handler.close()
        
        # Close and remove the temporary database file
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
        # Remove the temporary upload folder and its contents
        shutil.rmtree(self.upload_folder)

    # Helper to log in a user
    def login(self, user_id="12345678"):
        with self.client.session_transaction() as sess:
            sess['user_id'] = int(user_id)
            sess['last_activity'] = datetime.now().isoformat()

    # --- Test Cases Will Go Here ---

    def test_manage_products_get_no_products(self):
        self.login()
        response = self.client.get('/manage_products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<h1>Produkte verwalten</h1>", response.data)
        self.assertIn(b"Keine Produkte vorhanden", response.data) # Check for message when no products

    def test_manage_products_get_with_products(self):
        # Add a product directly via db_handler for setup
        self.test_db_handler.create_product("Test Drink", 10, 1.99, "test_drink.png")
        self.login()
        
        response = self.client.get('/manage_products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Drink", response.data)
        self.assertIn(b"1.99", response.data) # Price
        self.assertIn(b"10", response.data) # Stock
        self.assertIn(b"images/test_drink.png", response.data) # Image reference

    def test_add_new_product_with_image(self):
        self.login()
        data = {
            'action': 'create',
            'name': 'Super Energy X',
            'price': '3.99',
            'amount': '50', # Initial stock
            'image': (BytesIO(b"fakeimagecontent"), 'super_x.png')
        }
        response = self.client.post('/manage_products', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302) # Redirect expected
        self.assertEqual(response.location, '/manage_products')

        # Verify in database
        product_db = self.test_db_handler.get_product_details_by_name('Super Energy X')
        self.assertIsNotNone(product_db)
        self.assertEqual(product_db['price'], 3.99)
        self.assertEqual(product_db['current_amount'], 50)
        self.assertEqual(product_db['image_filename'], 'super_x.png')

        # Verify image saved
        self.assertTrue(os.path.exists(os.path.join(self.upload_folder, 'super_x.png')))

    def test_add_new_product_no_image(self):
        self.login()
        data = {
            'action': 'create',
            'name': 'Plain Water',
            'price': '1.00',
            'amount': '100',
            # No image file submitted
        }
        response = self.client.post('/manage_products', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/manage_products')

        product_db = self.test_db_handler.get_product_details_by_name('Plain Water')
        self.assertIsNotNone(product_db)
        self.assertEqual(product_db['image_filename'], 'default.png') # Should use default
        self.assertFalse(os.path.exists(os.path.join(self.upload_folder, 'default.png'))) # Default shouldn't be "saved" by this action specifically

    def test_increment_stock(self):
        p = self.test_db_handler.create_product("Test Increment", 5, 1.0, "inc.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test Increment")['id']
        self.login()
        
        response = self.client.post(f'/product/increment_stock/{product_id}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/manage_products')
        
        product_db = self.test_db_handler.get_product_details(product_id)
        self.assertEqual(product_db['current_amount'], 6)

    def test_decrement_stock(self):
        self.test_db_handler.create_product("Test Decrement", 5, 1.0, "dec.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test Decrement")['id']
        self.login()

        response = self.client.post(f'/product/decrement_stock/{product_id}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/manage_products')

        product_db = self.test_db_handler.get_product_details(product_id)
        self.assertEqual(product_db['current_amount'], 4)

    def test_decrement_stock_at_zero(self):
        self.test_db_handler.create_product("Test Decrement Zero", 0, 1.0, "deczero.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test Decrement Zero")['id']
        self.login()

        response = self.client.post(f'/product/decrement_stock/{product_id}')
        self.assertEqual(response.status_code, 302)
        product_db = self.test_db_handler.get_product_details(product_id)
        self.assertEqual(product_db['current_amount'], 0) # Should not go below zero

    def test_update_stock_directly(self):
        self.test_db_handler.create_product("Test UpdateDirect", 10, 1.0, "upd.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test UpdateDirect")['id']
        self.login()

        response = self.client.post(f'/product/update_stock/{product_id}', data={'new_stock': '25'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/manage_products')

        product_db = self.test_db_handler.get_product_details(product_id)
        self.assertEqual(product_db['current_amount'], 25)
        
    def test_update_stock_directly_negative(self):
        self.test_db_handler.create_product("Test UpdateDirectNeg", 10, 1.0, "updneg.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test UpdateDirectNeg")['id']
        self.login()

        response = self.client.post(f'/product/update_stock/{product_id}', data={'new_stock': '-5'})
        self.assertEqual(response.status_code, 302) # Redirects
        # Check flash message or that stock is NOT -5
        product_db = self.test_db_handler.get_product_details(product_id)
        self.assertNotEqual(product_db['current_amount'], -5) # Should be handled by app logic
        self.assertIn(b"Lagerbestand kann nicht negativ sein.", self.client.get('/manage_products').data)


    def test_delete_product_with_image(self):
        self.test_db_handler.create_product("Test Delete Me", 1, 1.0, "delete_me.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test Delete Me")['id']
        # Create a dummy image file
        dummy_image_path = os.path.join(self.upload_folder, "delete_me.png")
        with open(dummy_image_path, 'wb') as f:
            f.write(b"dummyimagedata")
        self.assertTrue(os.path.exists(dummy_image_path))
        
        self.login()
        response = self.client.post(f'/product/delete/{product_id}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/manage_products')

        self.assertIsNone(self.test_db_handler.get_product_details(product_id))
        self.assertFalse(os.path.exists(dummy_image_path)) # Image should be deleted

    def test_delete_product_default_image(self):
        self.test_db_handler.create_product("Test Delete Default", 1, 1.0, "default.png")
        product_id = self.test_db_handler.get_product_details_by_name("Test Delete Default")['id']
        
        # Ensure default.png is NOT in the dynamic UPLOAD_FOLDER before test
        default_image_path_in_uploads = os.path.join(self.upload_folder, "default.png")
        if os.path.exists(default_image_path_in_uploads):
             os.remove(default_image_path_in_uploads)

        self.login()
        response = self.client.post(f'/product/delete/{product_id}')
        self.assertEqual(response.status_code, 302)

        self.assertIsNone(self.test_db_handler.get_product_details(product_id))
        # Default image should not be deleted from UPLOAD_FOLDER (as it wasn't there, or if it was, app shouldn't delete it)
        self.assertFalse(os.path.exists(default_image_path_in_uploads))


if __name__ == '__main__':
    from datetime import datetime # For login helper session
    from io import BytesIO # For file uploads
    # Add a helper method to DBHandler in testing context or here for get_product_details_by_name
    def get_product_details_by_name(self, name):
        self.cursor.execute("SELECT id, name, current_amount, price, image_filename FROM products WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'current_amount': row[2], 'price': row[3], 'image_filename': row[4]}
        return None
    DBHandler.get_product_details_by_name = get_product_details_by_name
    
    unittest.main()
