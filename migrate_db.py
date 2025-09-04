import sqlite3
from datetime import datetime
import shutil

# Backup the old database
shutil.copy2('energy_drinks.db', 'energy_drinks_backup.db')

# Connect to the database
conn = sqlite3.connect('energy_drinks.db')
cursor = conn.cursor()

# Create the new transaction_history table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_type TEXT NOT NULL,
        user_id INTEGER,
        product_id INTEGER,
        amount REAL NOT NULL,
        description TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Migrate existing purchase history to transaction history
cursor.execute('SELECT product_id, user_id, amount, purchase_date FROM purchase_history')
purchases = cursor.fetchall()

for product_id, user_id, amount, purchase_date in purchases:
    # Get the price at the time (using current price as we don't have historical prices)
    cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
    price = cursor.fetchone()[0]
    total_cost = price * amount
    
    cursor.execute('''
        INSERT INTO transaction_history 
        (transaction_type, user_id, product_id, amount, description, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('PURCHASE', user_id, product_id, amount, f"Purchase at €{total_cost}", purchase_date))

print(f"Migrated {len(purchases)} purchase records")

# Commit changes and close connection
conn.commit()
conn.close()

print("Migration completed successfully!")
print("A backup of your original database was created as 'energy_drinks_backup.db'")