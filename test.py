import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
from ui_test import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.warenkorb = []

        # Connect buttons to addItem method
        self.ui.pushButton_mango_loco.clicked.connect(lambda: self.addItem("Mango Loco"))
        self.ui.pushButton_assaulted.clicked.connect(lambda: self.addItem("Assaulted"))
        self.ui.pushButton_ultra_fiesta.clicked.connect(lambda: self.addItem("Ultra Fiesta"))
        self.ui.pushButton_bad_apple.clicked.connect(lambda: self.addItem("Bad Apple"))

    def addItem(self, flavor):
        self.warenkorb.append(flavor)
        self.ui.textBrowser_warenkorb.append(flavor)
        print(f"{flavor} added")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())