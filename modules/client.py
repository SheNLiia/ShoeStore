import pymysql
from PyQt6.QtGui import QPixmap
from modules.database import db
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic


class ClientWindow(QMainWindow):
    def __init__(self, role_name=None, user_fio=None, user_id=None):
        super().__init__()

        uic.loadUi("ui/client.ui", self)

        self.user_id = user_id
        self.role_name = role_name
        self.user_fio = user_fio

        if user_id is None:
            self.setWindowTitle("Окно гостя")
            self.label_role.setText("Гость")
        else:
            self.label_role.setText(f"{role_name}: {user_fio}")

        self.pushButton_exit_menu.clicked.connect(self.logout)

        self.load_menu()

    def load_menu(self):
        # Очищаю текущий список товаров перед повторной загрузкой
        for i in reversed(range(self.verticalLayout_menu.count())):
            self.verticalLayout_menu.itemAt(i).widget().setParent(None)

        try:
            items = db.fetch_all("""
                                 SELECT p.*, c.category_name, m.manufacturer_name, s.supplier_name
                                 FROM products p
                                          LEFT JOIN categories c ON c.category_id = p.category_id
                                          LEFT JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
                                          LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id
                                 """)
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        for item in items:
            widget = uic.loadUi("ui/widget_menu.ui")

            widget.label_category_name.setText(f"{item['category_name']} | {item['product_name']}")
            widget.label_description.setText(f"Описание: {item['description']}")
            widget.label_manufacturer_name.setText(f"Производитель: {item['manufacturer_name']}")
            widget.label_supplier_name.setText(f"Поставщик: {item['supplier_name']}")
            widget.label_price.setText(f"Цена: {item['price']} рублей")
            widget.label_unit.setText(f"Единица измерения: {item['unit']}")
            widget.label_stock_quantity.setText(f"Количество на складе: {item['stock_quantity']}")

            discount = item["discount_percentage"] or 0
            widget.label_discount_percentage.setText(f"Скидка: {int(discount)}%")

            image_path = item["image_path"]

            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                pixmap_placeholder = QPixmap("images/picture.png")
                pixmap_placeholder = pixmap_placeholder.scaled(300, 200)
                widget.label_photo.setPixmap(pixmap_placeholder)
            else:
                pixmap = pixmap.scaled(300, 200)
                widget.label_photo.setPixmap(pixmap)

            price = int(item['price'])

            if discount > 0:
                new_price = price - (price * discount / 100)

                widget.label_price.setText(
                    f"Цена: <s><font color='red'>{item['price']}</font></s> "
                    f"{new_price:.2f} рублей"
                )

            if discount > 15:
                widget.setStyleSheet("background-color: #2E8B57")

            if item["stock_quantity"] == 0:
                widget.setStyleSheet(
                    "background-color: lightblue"
                )

            self.verticalLayout_menu.addWidget(widget)

    def logout(self):
        from modules.auth import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()
