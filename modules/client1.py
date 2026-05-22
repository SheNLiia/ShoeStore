import sys
import traceback

import pymysql
from PyQt6.QtGui import QPixmap
from modules.database import db
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("ui/client.ui", self)

        self.load_menu()

        self.lineEdit_search.textChanged.connect(self.load_menu)

    def load_menu(self):
        for i in reversed(range(self.verticalLayout_menu.count())):
            self.verticalLayout_menu.itemAt(i).widget().setParent(None)

        search_text = self.lineEdit_search.text()

        try:
            items = db.fetch_all("""
                SELECT p.*
                FROM Products p
                WHERE p.product_name LIKE %s
            """, (f"%{search_text}%",))
        except pymysql.MySQLError as e:
            QMessageBox.warning(self, "Ошибка БД: ", str(e))
            return

        for i in items:
            widget = uic.loadUi("ui/widget_menu.ui")

            widget.label_city.setText(i['product_name'])
            widget.label_price.setText(f"{i['price']}")

            image_path = i['image_path']

            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                widget.label_photo.setText("Нет фото")
            else:
                pixmap = pixmap.scaled(150,150)
                widget.label_photo.setPixmap(pixmap)

            self.verticalLayout_menu.addWidget(widget)

    def a(b, c, d):
        traceback.print_exception(b, c, d)

    sys.excepthook = a

