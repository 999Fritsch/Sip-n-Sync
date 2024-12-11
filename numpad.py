# numpad.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout

class Numpad(QWidget):
    def __init__(self, input_field, enter_callback):
        super().__init__()
        self.input_field = input_field
        self.enter_callback = enter_callback
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('0', 3, 1), ('Del', 3, 0), ('Enter', 3, 2)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.clicked.connect(self.button_clicked)
            layout.addWidget(button, row, col)

        self.setLayout(layout)

    def button_clicked(self):
        button = self.sender()
        current_text = self.input_field.text()

        if button.text() == 'Del':
            new_text = current_text[:-1]
        elif button.text() == 'Enter':
            self.enter_callback()
            return
        else:
            new_text = current_text + button.text()

        self.input_field.setText(new_text)