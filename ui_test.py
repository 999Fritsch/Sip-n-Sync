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
    QTextEdit, QWidget)

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
        self.label_mango_loco = QLabel(self.centralwidget)
        self.label_mango_loco.setObjectName(u"label_mango_loco")
        self.label_mango_loco.setGeometry(QRect(100, 250, 221, 17))
        self.pushButton_mango_loco = QPushButton(self.centralwidget)
        self.pushButton_mango_loco.setObjectName(u"pushButton_mango_loco")
        self.pushButton_mango_loco.setGeometry(QRect(210, 250, 89, 25))
        self.label_assault = QLabel(self.centralwidget)
        self.label_assault.setObjectName(u"label_assault")
        self.label_assault.setGeometry(QRect(100, 310, 221, 17))
        self.pushButton_assaulted = QPushButton(self.centralwidget)
        self.pushButton_assaulted.setObjectName(u"pushButton_assaulted")
        self.pushButton_assaulted.setGeometry(QRect(210, 310, 89, 25))
        self.label_ultra_fiesta = QLabel(self.centralwidget)
        self.label_ultra_fiesta.setObjectName(u"label_ultra_fiesta")
        self.label_ultra_fiesta.setGeometry(QRect(100, 370, 221, 17))
        self.pushButton_ultra_fiesta = QPushButton(self.centralwidget)
        self.pushButton_ultra_fiesta.setObjectName(u"pushButton_ultra_fiesta")
        self.pushButton_ultra_fiesta.setGeometry(QRect(210, 370, 89, 25))
        self.label_bad_apple = QLabel(self.centralwidget)
        self.label_bad_apple.setObjectName(u"label_bad_apple")
        self.label_bad_apple.setGeometry(QRect(100, 430, 221, 17))
        self.pushButton_bad_apple = QPushButton(self.centralwidget)
        self.pushButton_bad_apple.setObjectName(u"pushButton_bad_apple")
        self.pushButton_bad_apple.setGeometry(QRect(210, 430, 89, 25))
        self.textBrowser_warenkorb = QTextBrowser(self.centralwidget)
        self.textBrowser_warenkorb.setObjectName(u"textBrowser_warenkorb")
        self.textBrowser_warenkorb.setGeometry(QRect(1240, 40, 351, 711))
        self.pushButton_bestellen = QPushButton(self.centralwidget)
        self.pushButton_bestellen.setObjectName(u"pushButton_bestellen")
        self.pushButton_bestellen.setGeometry(QRect(1280, 800, 281, 91))
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
        self.label_mango_loco.setText(QCoreApplication.translate("MainWindow", u"Mango Loco", None))
        self.pushButton_mango_loco.setText(QCoreApplication.translate("MainWindow", u"add", None))
        self.label_assault.setText(QCoreApplication.translate("MainWindow", u"Assaulted :,(", None))
        self.pushButton_assaulted.setText(QCoreApplication.translate("MainWindow", u"add", None))
        self.label_ultra_fiesta.setText(QCoreApplication.translate("MainWindow", u"Ultra Fiesta", None))
        self.pushButton_ultra_fiesta.setText(QCoreApplication.translate("MainWindow", u"add", None))
        self.label_bad_apple.setText(QCoreApplication.translate("MainWindow", u"Bad Apple", None))
        self.pushButton_bad_apple.setText(QCoreApplication.translate("MainWindow", u"add", None))
        self.pushButton_bestellen.setText(QCoreApplication.translate("MainWindow", u"bestellen", None))
    # retranslateUi

