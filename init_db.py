import sqlite3

def initialize_database():
    # Verbindung zur SQLite-Datenbank herstellen (oder erstellen, falls sie nicht existiert)
    conn = sqlite3.connect('energy_drinks.db')
    cursor = conn.cursor()

    # Tabelle products erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            current_amount INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Tabelle users erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            money_amount REAL NOT NULL
        )
    ''')

    # Benutzer "ZugKasse" hinzufügen
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, name, money_amount) VALUES (69, 'ZugKasse', 0)
    ''')

    # Tabelle purchase_history erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Tabelle transaction_history erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,  -- 'PURCHASE', 'DEPOSIT', 'REFILL', 'NEW_PRODUCT', 'NEW_USER', 'ADD_MONEY'
            user_id INTEGER,                 -- NULL for NEW_PRODUCT
            product_id INTEGER,              -- NULL for NEW_USER, ADD_MONEY, DEPOSIT
            amount REAL NOT NULL,            -- Amount of products or money
            description TEXT,                -- Additional details (e.g., product name for NEW_PRODUCT)
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()