# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextBrowser,
    QTextEdit, QWidget, QVBoxLayout, QHBoxLayout)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1623, 981)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.textEdit_id = QTextEdit(self.centralwidget)
        self.textEdit_id.setObjectName(u"textEdit_id")
        self.textEdit_id.setGeometry(QRect(20, 30, 451, 71))
        self.dynamicWidget = QWidget(self.centralwidget)
        self.dynamicWidget.setObjectName(u"dynamicWidget")
        self.dynamicWidget.setGeometry(QRect(20, 120, 600, 600))
        self.textBrowser_warenkorb = QTextBrowser(self.centralwidget)
        self.textBrowser_warenkorb.setObjectName(u"textBrowser_warenkorb")
        self.textBrowser_warenkorb.setGeometry(QRect(1240, 40, 351, 711))
        self.pushButton_bestellen = QPushButton(self.centralwidget)
        self.pushButton_bestellen.setObjectName(u"pushButton_bestellen")
        self.pushButton_bestellen.setGeometry(QRect(1280, 800, 281, 91))
        self.label_id_confirmation = QLabel(self.centralwidget)
        self.label_id_confirmation.setObjectName(u"label_id_confirmation")
        self.label_id_confirmation.setGeometry(QRect(20, 110, 451, 21))
        self.label_id_confirmation.setStyleSheet("color: red;")
        self.label_order_confirmation = QLabel(self.centralwidget)
        self.label_order_confirmation.setObjectName(u"label_order_confirmation")
        self.label_order_confirmation.setGeometry(QRect(20, 900, 451, 21))
        self.label_order_confirmation.setStyleSheet("color: green;")
        self.label_order_confirmation.setText("")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1623, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_bestellen.setText(QCoreApplication.translate("MainWindow", u"bestellen", None))
        self.label_id_confirmation.setText("")
    # retranslateUi

    def add_dynamic_widgets(self, MainWindow, products):
        layout = QVBoxLayout(self.dynamicWidget)
        for product in products:
            product_layout = QHBoxLayout()
            
            label = QLabel(self.dynamicWidget)
            label.setText(product['name'])
            product_layout.addWidget(label)
            
            button_add = QPushButton(self.dynamicWidget)
            button_add.setText("add")
            button_add.clicked.connect(lambda _, p=product: MainWindow.addItem(p['name']))
            product_layout.addWidget(button_add)
            
            button_remove = QPushButton(self.dynamicWidget)
            button_remove.setText("remove")
            button_remove.clicked.connect(lambda _, p=product: MainWindow.removeItem(p['name']))
            product_layout.addWidget(button_remove)
            
            layout.addLayout(product_layout)
        self.dynamicWidget.setLayout(layout)

