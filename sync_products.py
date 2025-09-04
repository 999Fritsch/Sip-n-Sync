import os
import sqlite3
from pathlib import Path

def title_case(text):
    """Convert text to title case (first letter of each word capitalized)."""
    return ' '.join(word.capitalize() for word in text.split())

def connect_db():
    """Create a connection to the SQLite database."""
    return sqlite3.connect('energy_drinks.db')

def get_image_products(image_dir='product_images'):
    """Get products from image files, converting underscores to spaces with title case."""
    image_products = []
    
    for ext in ('*.jpg', '*.jpeg', '*.png'):
        image_products.extend(Path(image_dir).glob(ext))
    
    # Convert to title case and replace underscores with spaces
    return {title_case(p.stem.replace('_', ' ')): p.stem for p in image_products}

def get_db_products(conn):
    """Get existing products from database."""
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM products')
    return {row[1]: row[0] for row in cursor.fetchall()}

def add_new_product(conn, name):
    """Add a new product to the database with default price 1.20."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, current_amount, price)
        VALUES (?, 0, 1.20)
    ''', (name,))
    
    product_id = cursor.lastrowid
    cursor.execute('''
        INSERT INTO transaction_history 
        (transaction_type, product_id, amount, description)
        VALUES (?, ?, ?, ?)
    ''', ('NEW_PRODUCT', product_id, 0, f"New product created from image: {name}"))
    
    conn.commit()
    return product_id

def update_product_name(conn, product_id, new_name):
    """Update existing product name in database with title case."""
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET name = ? WHERE id = ?', (new_name, product_id))
    
    cursor.execute('''
        INSERT INTO transaction_history 
        (transaction_type, product_id, amount, description)
        VALUES (?, ?, ?, ?)
    ''', ('UPDATE_PRODUCT', product_id, 0, f"Updated product name to: {new_name}"))
    
    conn.commit()

def main():
    if not os.path.exists('product_images'):
        print("Error: 'products' directory not found!")
        return

    conn = connect_db()
    
    try:
        image_products = get_image_products()
        db_products = get_db_products(conn)
        
        added = []
        updated = []
        
        for display_name, file_name in image_products.items():
            if display_name not in db_products:
                add_new_product(conn, display_name)
                added.append(display_name)
            else:
                product_id = db_products[display_name]
                if display_name != file_name.replace('_', ' ').upper():
                    update_product_name(conn, product_id, display_name)
                    updated.append(f"{file_name} -> {display_name}")
        
        if added:
            print("\nAdded new products:")
            for name in added:
                print(f"  - {name}")
        
        if updated:
            print("\nUpdated product names:")
            for update in updated:
                print(f"  - {update}")
        
        if not (added or updated):
            print("\nNo changes needed - all products are synchronized.")
            
    finally:
        conn.close()

if __name__ == '__main__':
    main()