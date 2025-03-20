import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta

# Add these constants at the top of your file
SESSION_TIMEOUT = 60  # seconds
LOGIN_REQUIRED_ROUTES = ['index', 'add_money', 'manage_products']  # routes that require login

# Add this decorator function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Bitte melden Sie sich zuerst an', 'error')
            return redirect(url_for('login'))
        
        # Check if session has expired
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(seconds=SESSION_TIMEOUT):
                session.clear()
                flash('Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an', 'info')
                return redirect(url_for('login'))
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Database Handler Definition
# ---------------------------
class DBHandler:
    def __init__(self, db_name='energy_drinks.db'):
        self.connect(db_name)
        self.map_flavor_to_id()

    def connect(self, db_name='energy_drinks.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)  # note: check_same_thread=False for Flask
        self.cursor = self.conn.cursor()

    def fetch_products(self):
        """Fetches product id and name from the database."""
        self.cursor.execute('SELECT id, name FROM products')
        products = self.cursor.fetchall()
        # Return a list of dictionaries for easier template usage.
        return [{'id': p[0], 'name': p[1]} for p in products]

    def map_flavor_to_id(self):
        """Maps product flavors to their corresponding IDs."""
        self.cursor.execute('SELECT id, name FROM products')
        products = self.cursor.fetchall()
        self.flavors = {name: product_id for product_id, name in products}
        return self.flavors

    def buy_energy_by_id(self, user_id, product_id, amount):
        """Processes the purchase of an energy drink by product ID."""
        self.cursor.execute('SELECT current_amount, price FROM products WHERE id = ?', (product_id,))
        product = self.cursor.fetchone()
        if product is None:
            raise ValueError("Produkt nicht gefunden")

        current_amount, price = product
        # if current_amount < amount:
        #     raise ValueError("Nicht genügend Produkt auf Lager")

        self.cursor.execute('SELECT money_amount FROM users WHERE id = ?', (user_id,))
        user = self.cursor.fetchone()
        if user is None:
            raise ValueError("Benutzer nicht gefunden")

        money_amount = user[0]
        total_cost = price * amount

        # Update product stock and user money
        self.cursor.execute('UPDATE products SET current_amount = current_amount - ? WHERE id = ?', (amount, product_id))
        self.cursor.execute('UPDATE users SET money_amount = money_amount - ? WHERE id = ?', (total_cost, user_id))
        self.cursor.execute('INSERT INTO purchase_history (product_id, user_id, amount) VALUES (?, ?, ?)', (product_id, user_id, amount))
        self.log_transaction('PURCHASE', user_id=user_id, product_id=product_id, amount=amount, description=f"Purchase at €{total_cost}")
        self.conn.commit()

    def buy_energy_by_flavor(self, user_id, flavor_name, amount):
        """Processes a purchase by flavor name."""
        if flavor_name not in self.flavors:
            raise KeyError(f"Flavor '{flavor_name}' not found")
        product_id = self.flavors[flavor_name]
        self.buy_energy_by_id(user_id, product_id, amount)

    def check_user_id(self, user_id):
        """Checks if a user id exists in the database."""
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] > 0

    def close(self):
        self.conn.close()

    def create_user(self, user_id, name, money_amount):
        """Creates a new user in the database."""
        self.cursor.execute('INSERT OR IGNORE INTO users (id, name, money_amount) VALUES (?, ?, ?)', (user_id, name, money_amount))
        self.log_transaction('NEW_USER', user_id=user_id, amount=money_amount, description=f"New user created: {name}")
        self.conn.commit()

    def create_product(self, name, current_amount, price):
        """Inserts a new product into the products table."""
        self.cursor.execute('INSERT INTO products (name, current_amount, price) VALUES (?, ?, ?)', (name, current_amount, price))
        product_id = self.cursor.lastrowid
        self.log_transaction('NEW_PRODUCT', product_id=product_id, amount=current_amount, description=f"New product created: {name} at €{price}")
        self.conn.commit()

    def add_product_storage(self, product_id, amount):
        """Adds the specified amount to the current storage of the product."""
        self.cursor.execute('UPDATE products SET current_amount = current_amount + ? WHERE id = ?', (amount, product_id))
        self.log_transaction('REFILL', product_id=product_id, amount=amount)
        self.conn.commit()

    def add_money_to_user(self, user_id, amount):
        """Adds the specified amount of money to the user's account."""
        self.cursor.execute('UPDATE users SET money_amount = money_amount + ? WHERE id = ?', (amount, user_id))
        self.log_transaction('ADD_MONEY', user_id=user_id, amount=amount)
        self.conn.commit()

    def log_transaction(self, transaction_type, user_id=None, product_id=None, amount=0, description=None):
        """Logs any transaction in the transaction_history table."""
        self.cursor.execute('''
            INSERT INTO transaction_history 
            (transaction_type, user_id, product_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (transaction_type, user_id, product_id, amount, description))
        self.conn.commit()

    def get_user_info(self, user_id):
        """Fetches user name and balance from the database."""
        self.cursor.execute('SELECT name, money_amount FROM users WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {'name': result[0], 'balance': result[1]}
        return None

    def get_user_transactions(self, user_id):
        """Fetches all transactions for a specific user."""
        self.cursor.execute('''
            SELECT 
                th.transaction_type,
                COALESCE(p.name, '') as product_name,
                th.amount,
                th.description,
                th.timestamp
            FROM transaction_history th
            LEFT JOIN products p ON th.product_id = p.id
            WHERE th.user_id = ?
            ORDER BY th.timestamp DESC
        ''', (user_id,))
        
        transactions = self.cursor.fetchall()
        return [
            {
                'type': t[0],
                'product': t[1],
                'amount': t[2],
                'description': t[3],
                'timestamp': t[4]
            }
            for t in transactions
        ]


# ---------------------------
# Flask App Setup
# ---------------------------
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

# Initialize the database handler
db_handler = DBHandler()


# ---------------------------
# Routes
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        
        try:
            int_user_id = int(user_id)
            if user_id == "" or (len(user_id) < 8 and int_user_id != 69):
                flash("Bitte gültige ID eingeben", "error")
                return redirect(url_for("login"))
                
            if not db_handler.check_user_id(int_user_id):
                flash("ID existiert nicht in der Datenbank", "error")
                return redirect(url_for("login"))
                
            session['user_id'] = int_user_id
            session['last_activity'] = datetime.now().isoformat()
            flash("Erfolgreich angemeldet!", "success")
            return redirect(url_for("index"))
            
        except ValueError:
            flash("Bitte gültige ID eingeben", "error")
            return redirect(url_for("login"))
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Erfolgreich abgemeldet", "success")
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Remove user_id validation from POST handling since it's now handled by the session
    if "cart" not in session:
        session["cart"] = {}

    if request.method == "POST":
        action = request.form.get("action")
        flavor = request.form.get("flavor")
        
        if action == "add" and flavor:
            cart = session["cart"]
            cart[flavor] = cart.get(flavor, 0) + 1
            session["cart"] = cart
            flash(f"{flavor} wurde hinzugefügt.", "info")
        elif action == "remove" and flavor:
            cart = session["cart"]
            if flavor in cart:
                if cart[flavor] > 1:
                    cart[flavor] -= 1
                else:
                    cart.pop(flavor)
                session["cart"] = cart
                flash(f"{flavor} wurde entfernt.", "info")
        elif action == "order":
            if not session["cart"]:
                flash("Bitte mindestens ein Getränk auswählen", "error")
                return redirect(url_for("index"))

            try:
                for flavor_name, amount in session["cart"].items():
                    db_handler.buy_energy_by_flavor(session['user_id'], flavor_name, amount)
                session["cart"] = {}
                flash("Bestellung erfolgreich!", "success")
            except Exception as e:
                flash(str(e), "error")

        return redirect(url_for("index"))

    products = db_handler.fetch_products()
    cart = session.get("cart", {})
    user_info = db_handler.get_user_info(session['user_id'])
    return render_template("order.html", products=products, cart=cart, user_info=user_info)

@app.route("/add_money", methods=["GET", "POST"])
@login_required
def add_money():
    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        try:
            float_amount = float(amount)
            db_handler.add_money_to_user(session['user_id'], float_amount)
            flash(f"{float_amount}€ wurden erfolgreich zum Konto hinzugefügt!", "success")
        except ValueError:
            flash("Bitte gültigen Betrag eingeben", "error")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("add_money"))
    user_info = db_handler.get_user_info(session['user_id'])
    return render_template("add_money.html", user_info=user_info)

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        name = request.form.get("name", "").strip()
        initial_amount = request.form.get("initial_amount", "0").strip()

        # Validate input
        try:
            int_user_id = int(user_id)
            float_amount = float(initial_amount)
        except ValueError:
            flash("Bitte gültige ID und Betrag eingeben", "error")
            return redirect(url_for("add_user"))

        # Validate user ID format
        if user_id == "" or (len(user_id) < 8 and int_user_id != 69):
            flash("Bitte gültige ID eingeben (mindestens 8 Stellen)", "error")
            return redirect(url_for("add_user"))

        # Validate name
        if not name:
            flash("Bitte einen Namen eingeben", "error")
            return redirect(url_for("add_user"))

        # Check if user already exists
        if db_handler.check_user_id(int_user_id):
            flash("Diese ID existiert bereits", "error")
            return redirect(url_for("add_user"))

        # Create new user
        try:
            db_handler.create_user(int_user_id, name, float_amount)
            flash(f"Benutzer {name} wurde erfolgreich erstellt!", "success")
        except Exception as e:
            flash(str(e), "error")

        return redirect(url_for("add_user"))

    return render_template("add_user.html")


@app.route("/manage_products", methods=["GET", "POST"])
@login_required
def manage_products():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            name = request.form.get("name", "").strip()
            amount = request.form.get("amount", "").strip()
            price = request.form.get("price", "").strip()

            # Validate input
            try:
                float_amount = float(amount)
                float_price = float(price)
            except ValueError:
                flash("Bitte gültige Werte für Menge und Preis eingeben", "error")
                return redirect(url_for("manage_products"))

            if not name:
                flash("Bitte einen Produktnamen eingeben", "error")
                return redirect(url_for("manage_products"))

            # Create new product
            try:
                db_handler.create_product(name, float_amount, float_price)
                flash(f"Produkt {name} wurde erfolgreich erstellt!", "success")
                # Refresh flavor mappings after creating new product
                db_handler.map_flavor_to_id()
            except Exception as e:
                flash(str(e), "error")

        elif action == "refill":
            product_id = request.form.get("product_id")
            amount = request.form.get("refill_amount", "").strip()

            # Validate input
            try:
                int_product_id = int(product_id)
                float_amount = float(amount)
            except ValueError:
                flash("Bitte gültige Werte eingeben", "error")
                return redirect(url_for("manage_products"))

            # Add to stock
            try:
                db_handler.add_product_storage(int_product_id, float_amount)
                flash(f"Lagerbestand wurde um {float_amount} erhöht!", "success")
            except Exception as e:
                flash(str(e), "error")

        elif action == "deposit":
            amount = request.form.get("deposit_amount", "").strip()

            # Validate input
            try:
                float_amount = float(amount)
                if float_amount <= 0:
                    raise ValueError()
            except ValueError:
                flash("Bitte gültigen Pfandbetrag eingeben", "error")
                return redirect(url_for("manage_products"))

            # Add deposit to Zugkasse (ID 69)
            try:
                db_handler.add_money_to_user(69, float_amount)
                flash(f"Pfand in Höhe von {float_amount}€ wurde zur Zugkasse hinzugefügt!", "success")
            except Exception as e:
                flash(str(e), "error")

        return redirect(url_for("manage_products"))

    # For GET request: fetch products from the database
    products = db_handler.fetch_products()
    user_info = db_handler.get_user_info(session['user_id'])
    return render_template("manage_products.html", products=products, user_info=user_info)

# Add this new route
@app.route("/transaction_history")
@login_required
def transaction_history():
    transactions = db_handler.get_user_transactions(session['user_id'])
    user_info = db_handler.get_user_info(session['user_id'])
    return render_template("transaction_history.html", 
                         transactions=transactions,
                         user_info=user_info)

# ---------------------------
# Run the App
# ---------------------------
if __name__ == "__main__":
    app.config.update(
        PERMANENT_SESSION_LIFETIME=timedelta(seconds=SESSION_TIMEOUT),
        SESSION_REFRESH_EACH_REQUEST=True
    )
    app.run(debug=True)
