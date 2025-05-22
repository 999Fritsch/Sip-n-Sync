import sqlite3

def create_products_table_if_not_exists(cursor):
    """
    Creates the 'products' table if it doesn't already exist.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            current_amount INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    print("Ensured 'products' table exists.")

def migrate_database(db_name='energy_drinks.db'):
    """
    Creates the 'products' table if it doesn't exist, then
    adds an 'image_filename' column to the 'products' table in the specified database
    if it doesn't already exist.

    Args:
        db_name (str): The name of the database file.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Step 1: Ensure the products table exists
        create_products_table_if_not_exists(cursor)

        # Step 2: Add the image_filename column if it doesn't exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'image_filename' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN image_filename TEXT DEFAULT 'default.png'")
            print("Database migration successful: 'image_filename' column added to 'products' table.")
        else:
            print("'image_filename' column already exists in 'products' table.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database migration failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate_database()
