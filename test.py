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

    def order(self):
        id = self.ui.textEdit_id.toPlainText()
        if id == "" or id.__len__() < 8:
            print("Bitte  gültige ID eingeben")
        elif self.warenkorb.__len__() == 0:
            print("Bitte mindestens ein Getränk auswählen")
        else:
            print(f"Bestellung für ID: {id} aufgegeben")
            for flavor, amount in self.warenkorb.items():
                self.DBHandler.buy_energy_by_flavor(id, flavor, amount)
            self.warenkorb = {}
            self.ui.textBrowser_warenkorb.setText("")
            print("Bestellt")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())