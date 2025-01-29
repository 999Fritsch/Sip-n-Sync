import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
from ui_test import Ui_MainWindow
from db_handler import DBHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.warenkorb = {}
        self.DBHandler = DBHandler()

        # Fetch products from the database
        products = self.fetch_products()
        self.ui.add_dynamic_widgets(self, products)

        # Connect bestellen button to order method
        self.ui.pushButton_bestellen.clicked.connect(self.order)
        
        # Connect textEdit_id textChanged signal to check_id method
        self.ui.textEdit_id.textChanged.connect(self.check_id)

    def fetch_products(self):
        self.DBHandler.cursor.execute('SELECT id, name FROM products')
        products = self.DBHandler.cursor.fetchall()
        return [{'id': product[0], 'name': product[1]} for product in products]

    def addItem(self, flavor):
        if flavor in self.warenkorb.keys():
            self.warenkorb[flavor] += 1
        else:
            self.warenkorb[flavor] = 1
        
        # Build the formatted string
        formatted_text = "\n".join([f"{key} x{value}" for key, value in self.warenkorb.items()])
        
        self.ui.textBrowser_warenkorb.setText(formatted_text)

    def removeItem(self, flavor):
        if flavor in self.warenkorb.keys():
            if self.warenkorb[flavor] > 1:
                self.warenkorb[flavor] -= 1
            else:
                del self.warenkorb[flavor]
        
        # Build the formatted string
        formatted_text = "\n".join([f"{key} x{value}" for key, value in self.warenkorb.items()])
        
        self.ui.textBrowser_warenkorb.setText(formatted_text)

    def order(self):
        id = self.ui.textEdit_id.toPlainText()
        if id == "" or id.__len__() < 8 and int(id) != 69:
            print("Bitte  gültige ID eingeben")
        elif self.warenkorb.__len__() == 0:
            print("Bitte mindestens ein Getränk auswählen")
        else:
            print(f"Bestellung für ID: {id} aufgegeben")
            for flavor, amount in self.warenkorb.items():
                self.DBHandler.buy_energy_by_flavor(id, flavor, amount)
            self.warenkorb = {}
            self.ui.textBrowser_warenkorb.setText("")
            self.ui.textEdit_id.setText("")
            print("Bestellt")
            self.ui.label_order_confirmation.setText("Bestellung erfolgreich!")

    def check_id(self):
        user_id = self.ui.textEdit_id.toPlainText().strip()
        if user_id:
            if self.DBHandler.check_user_id(user_id):
                self.ui.label_id_confirmation.setText("ID exists in the database")
                self.ui.label_id_confirmation.setStyleSheet("color: green;")
                self.ui.label_order_confirmation.setText("")
            else:
                self.ui.label_id_confirmation.setText("ID does not exist in the database")
                self.ui.label_id_confirmation.setStyleSheet("color: red;")
                self.ui.label_order_confirmation.setText("")
        else:
            self.ui.label_id_confirmation.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())