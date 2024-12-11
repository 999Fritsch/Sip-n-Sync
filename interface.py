import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QMessageBox, QWidget
from PyQt6.QtCore import Qt
from numpad import Numpad

class LoginScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 400)

        self.textbox_user = QLineEdit(self)
        self.textbox_user.setPlaceholderText('Enter ID')
        self.textbox_user.setGeometry(50, 50, 200, 40)
        self.textbox_user.setMaxLength(8)
        self.textbox_user.textChanged.connect(self.on_text_changed)

        self.numpad = Numpad(self.textbox_user, self.check_login)
        self.numpad.setGeometry(50, 100, 200, 200)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.textbox_user)
        layout.addWidget(self.numpad)
        self.setCentralWidget(central_widget)

    def on_text_changed(self):
        if len(self.textbox_user.text()) == 8:
            self.check_login()

    def check_login(self):
        user_id = self.textbox_user.text()

        conn = sqlite3.connect('energy_drinks.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, 'Success', 'Login Successful')
        else:
            QMessageBox.warning(self, 'Error', 'Invalid ID')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec())