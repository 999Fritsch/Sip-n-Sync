import sqlite3
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from db_handler import DBHandler # Import DBHandler

# Add these constants at the top of your file
SESSION_TIMEOUT = 60  # seconds
LOGIN_REQUIRED_ROUTES = ['index', 'add_money', 'manage_products']  # routes that require login
UPLOAD_FOLDER = 'static/images'


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
# Flask App Setup
# ---------------------------
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create symlink from product_images to static/images (if product_images exists)
# This part might need adjustment based on actual project structure for product_images source
product_images_source_path = os.path.join(os.path.dirname(__file__), 'product_images')
static_images_symlink_path = os.path.join(app.static_folder, 'images') # app.static_folder is 'static'

# Check if product_images_source_path exists and is a directory
if os.path.isdir(product_images_source_path):
    # Check if the target static/images is not already a symlink or a directory
    if not os.path.islink(static_images_symlink_path) and not os.path.isdir(static_images_symlink_path):
        try:
            os.symlink(product_images_source_path, static_images_symlink_path, target_is_directory=True)
            print(f"Symlink created from {product_images_source_path} to {static_images_symlink_path}")
        except OSError as e:
            print(f"Error creating symlink: {e}")
    elif os.path.islink(static_images_symlink_path):
        print(f"Symlink {static_images_symlink_path} already exists.")
    elif os.path.isdir(static_images_symlink_path):
        print(f"Directory {static_images_symlink_path} already exists (not a symlink). Will use it for uploads.")
else:
    print(f"Source product_images directory '{product_images_source_path}' not found. Uploaded images will be saved directly in '{app.config['UPLOAD_FOLDER']}'.")


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

    # Use get_all_products_with_details to ensure image_filename is available for the template
    products = db_handler.get_all_products_with_details()
    cart = session.get("cart", {})
    user_info = db_handler.get_user_info(session['user_id'])
    # Note: The order.html template will need to be updated to use product.image_filename
    # and construct the path like url_for('static', filename='images/' + product.image_filename)
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
            amount = request.form.get("amount", "").strip() # This is current_amount / stock
            price = request.form.get("price", "").strip()
            image_file = request.files.get('image')
            image_filename = 'default.png'

            if not name:
                flash("Bitte einen Produktnamen eingeben", "error")
                return redirect(url_for("manage_products"))
            
            try:
                current_amount_int = int(amount)
                price_float = float(price)
            except ValueError:
                flash("Bitte gültige Werte für Menge und Preis eingeben", "error")
                return redirect(url_for("manage_products"))

            if image_file and image_file.filename != '':
                if '.' in image_file.filename and image_file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                    image_filename = secure_filename(image_file.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                    try:
                        image_file.save(image_path)
                    except Exception as e:
                        flash(f"Fehler beim Speichern des Bildes: {e}", "error")
                        return redirect(url_for("manage_products"))
                else:
                    flash("Ungültiges Bildformat. Nur PNG, JPG, JPEG, GIF erlaubt.", "error")
                    return redirect(url_for("manage_products"))
            
            try:
                db_handler.create_product(name, current_amount_int, price_float, image_filename)
                flash(f"Produkt {name} wurde erfolgreich erstellt!", "success")
                db_handler.map_flavor_to_id() # Refresh flavor map
            except Exception as e:
                flash(str(e), "error")
            return redirect(url_for("manage_products"))

        elif action == "refill": # Kept for now, might be replaced by update_stock
            product_id = request.form.get("product_id")
            amount = request.form.get("refill_amount", "").strip()

            try:
                int_product_id = int(product_id)
                float_amount_refill = float(amount) # Renamed to avoid conflict
            except ValueError:
                flash("Bitte gültige Werte eingeben für Refill", "error")
                return redirect(url_for("manage_products"))

            try:
                db_handler.add_product_storage(int_product_id, float_amount_refill)
                flash(f"Lagerbestand wurde um {float_amount_refill} erhöht!", "success")
            except Exception as e:
                flash(str(e), "error")
            return redirect(url_for("manage_products"))
            
        elif action == "deposit": # This action seems unrelated to product management directly
            amount_deposit = request.form.get("deposit_amount", "").strip() # Renamed
            try:
                float_amount_deposit = float(amount_deposit)
                if float_amount_deposit <= 0:
                    raise ValueError("Deposit amount must be positive")
            except ValueError:
                flash("Bitte gültigen Pfandbetrag eingeben", "error")
                return redirect(url_for("manage_products"))
            try:
                db_handler.add_money_to_user(69, float_amount_deposit) # Assuming user ID 69 is for "Zugkasse"
                flash(f"Pfand in Höhe von {float_amount_deposit}€ wurde zur Zugkasse hinzugefügt!", "success")
            except Exception as e:
                flash(str(e), "error")
            return redirect(url_for("manage_products"))

    # For GET request: fetch all products with details
    products = db_handler.get_all_products_with_details() # Updated to use new DB handler method
    user_info = db_handler.get_user_info(session['user_id'])
    return render_template("manage_products.html", products=products, user_info=user_info)

# New routes for product manipulation

@app.route("/product/update_stock/<int:product_id>", methods=["POST"])
@login_required
def update_product_stock_route(product_id):
    new_stock_str = request.form.get("new_stock")
    if new_stock_str is None:
        flash("Kein neuer Lagerbestand angegeben.", "error")
        return redirect(url_for("manage_products"))
    try:
        new_stock = int(new_stock_str)
        if new_stock < 0:
            flash("Lagerbestand kann nicht negativ sein.", "error")
        else:
            db_handler.update_product_stock(product_id, new_stock)
            flash("Lagerbestand erfolgreich aktualisiert.", "success")
    except ValueError:
        flash("Ungültiger Wert für Lagerbestand.", "error")
    except Exception as e:
        flash(f"Fehler beim Aktualisieren des Lagerbestands: {str(e)}", "error")
    return redirect(url_for("manage_products"))

@app.route("/product/increment_stock/<int:product_id>", methods=["POST"])
@login_required
def increment_product_stock_route(product_id):
    try:
        product = db_handler.get_product_details(product_id)
        if product:
            current_stock = product['current_amount']
            db_handler.update_product_stock(product_id, current_stock + 1)
            flash("Lagerbestand um 1 erhöht.", "success")
        else:
            flash("Produkt nicht gefunden.", "error")
    except Exception as e:
        flash(f"Fehler beim Erhöhen des Lagerbestands: {str(e)}", "error")
    return redirect(url_for("manage_products"))

@app.route("/product/decrement_stock/<int:product_id>", methods=["POST"])
@login_required
def decrement_product_stock_route(product_id):
    try:
        product = db_handler.get_product_details(product_id)
        if product:
            current_stock = product['current_amount']
            db_handler.update_product_stock(product_id, max(0, current_stock - 1))
            flash("Lagerbestand um 1 verringert.", "success")
        else:
            flash("Produkt nicht gefunden.", "error")
    except Exception as e:
        flash(f"Fehler beim Verringern des Lagerbestands: {str(e)}", "error")
    return redirect(url_for("manage_products"))

@app.route("/product/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product_route(product_id):
    try:
        product_details = db_handler.get_product_details(product_id)
        if product_details:
            image_filename_to_delete = product_details.get('image_filename')
            db_handler.delete_product(product_id)
            flash("Produkt erfolgreich gelöscht.", "success")

            if image_filename_to_delete and image_filename_to_delete != 'default.png':
                try:
                    image_path_to_delete = os.path.join(app.config['UPLOAD_FOLDER'], image_filename_to_delete)
                    if os.path.exists(image_path_to_delete):
                        os.remove(image_path_to_delete)
                        flash(f"Bild '{image_filename_to_delete}' wurde ebenfalls gelöscht.", "info")
                except Exception as e:
                    flash(f"Fehler beim Löschen des Produktbildes: {str(e)}", "warning")
            db_handler.map_flavor_to_id() # Refresh flavor map
        else:
            flash("Produkt nicht gefunden.", "error")
    except Exception as e:
        flash(f"Fehler beim Löschen des Produkts: {str(e)}", "error")
    return redirect(url_for("manage_products"))

@app.route("/transaction_history")
@login_required
def transaction_history():
    user_id = session.get('user_id')
    if user_id is None: # Should be caught by @login_required, but as a safeguard
        flash("Benutzer nicht angemeldet.", "error")
        return redirect(url_for('login'))
        
    transactions = db_handler.get_user_transactions(user_id)
    user_info = db_handler.get_user_info(user_id)
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
    # Make sure the UPLOAD_FOLDER exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    app.run(debug=True)
