import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

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
        if current_amount < amount:
            raise ValueError("Nicht genügend Produkt auf Lager")

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
@app.route("/", methods=["GET", "POST"])
def index():
    # Ensure that the cart (warenkorb) exists in the session
    if "cart" not in session:
        session["cart"] = {}  # Dictionary mapping flavor -> count

    if request.method == "POST":
        action = request.form.get("action")
        flavor = request.form.get("flavor")
        # --- Add an item ---
        if action == "add" and flavor:
            cart = session["cart"]
            cart[flavor] = cart.get(flavor, 0) + 1
            session["cart"] = cart
            flash(f"{flavor} wurde hinzugefügt.", "info")
        # --- Remove an item ---
        elif action == "remove" and flavor:
            cart = session["cart"]
            if flavor in cart:
                if cart[flavor] > 1:
                    cart[flavor] -= 1
                else:
                    cart.pop(flavor)
                session["cart"] = cart
                flash(f"{flavor} wurde entfernt.", "info")
        # --- Process the order ---
        elif action == "order":
            user_id = request.form.get("user_id", "").strip()
            # Validate user id similar to the PyQt logic:
            try:
                int_user_id = int(user_id)
            except ValueError:
                flash("Bitte gültige ID eingeben", "error")
                return redirect(url_for("index"))
            if user_id == "" or (len(user_id) < 8 and int_user_id != 69):
                flash("Bitte gültige ID eingeben", "error")
                return redirect(url_for("index"))
            if not session["cart"]:
                flash("Bitte mindestens ein Getränk auswählen", "error")
                return redirect(url_for("index"))

            # Optionally, check if the user exists:
            if not db_handler.check_user_id(int_user_id):
                flash("ID existiert nicht in der Datenbank", "error")
                return redirect(url_for("index"))

            # Process each item in the cart:
            try:
                for flavor_name, amount in session["cart"].items():
                    db_handler.buy_energy_by_flavor(int_user_id, flavor_name, amount)
                session["cart"] = {}  # Clear the cart on success
                flash("Bestellung erfolgreich!", "success")
            except Exception as e:
                flash(str(e), "error")
        return redirect(url_for("index"))

    # For GET request: fetch products from the database
    products = db_handler.fetch_products()
    cart = session.get("cart", {})
    return render_template("order.html", products=products, cart=cart)


# ---------------------------
# Run the App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
