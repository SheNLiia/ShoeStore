import pymysql
from PyQt6.QtGui import QPixmap
from modules.database import db
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic

class ManagerWindow(QMainWindow):
    def __init__(self, role_name=None, user_fio=None):
        super().__init__()

        uic.loadUi("ui/manager.ui", self)

        self.role_name = role_name
        self.user_fio = user_fio

        self.label_role.setText(f"{role_name}: {user_fio}")

        self.pushButton_exit.clicked.connect(self.logout)
        self.comboBox_sort.currentTextChanged.connect(self.sort_menu)
        self.lineEdit_search.textChanged.connect(self.sort_menu)
        self.comboBox_sort_suppliers.currentTextChanged.connect(self.sort_menu)
        self.pushButton_order.clicked.connect(self.show_orders)

        self.load_menu()
        self.load_suppliers()

    def load_menu(self, text="DESC", supplier="Все поставщики", search_text=""):
        for i in reversed(range(self.verticalLayout_menu.count())):
            self.verticalLayout_menu.itemAt(i).widget().setParent(None)

        try:
            if supplier == "Все поставщики":
                items = db.fetch_all(f"""
                    SELECT p.*, c.category_name, m.manufacturer_name, s.supplier_name
                    FROM Products p
                             LEFT JOIN Categories c ON c.category_id = p.category_id
                             LEFT JOIN Manufacturers m ON m.manufacturer_id = p.manufacturer_id
                             LEFT JOIN Suppliers s ON s.supplier_id = p.supplier_id
                    WHERE p.product_name LIKE %s
                       OR p.description LIKE %s
                       OR c.category_name LIKE %s
                       OR m.manufacturer_name LIKE %s
                       OR s.supplier_name LIKE %s
                    ORDER BY p.stock_quantity {text}
                    """, (
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%"
                ))

            else:
                items = db.fetch_all(f"""
                    SELECT p.*, c.category_name, m.manufacturer_name, s.supplier_name
                    FROM Products p
                             LEFT JOIN Categories c ON c.category_id = p.category_id
                             LEFT JOIN Manufacturers m ON m.manufacturer_id = p.manufacturer_id
                             LEFT JOIN Suppliers s ON s.supplier_id = p.supplier_id
                    WHERE s.supplier_name = %s
                      AND (
                        p.product_name LIKE %s
                            OR p.description LIKE %s
                            OR c.category_name LIKE %s
                            OR m.manufacturer_name LIKE %s
                        )
                    ORDER BY p.stock_quantity {text}
                """, (
                    supplier,
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%"
                ))

        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
            return

        for item in items:
            widget = uic.loadUi("ui/widget_menu.ui")

            widget.product_name = item['product_name']

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
                widget.setStyleSheet("background-color: lightblue")

            self.verticalLayout_menu.addWidget(widget)

    def sort_menu(self):
        supplier = self.comboBox_sort_suppliers.currentText()
        search_text = self.lineEdit_search.text()
        sort_text = self.comboBox_sort.currentText()

        if sort_text == "Количество (по убыванию)":
            sort = "DESC"
        else:
            sort = "ASC"

        self.load_menu(sort, supplier, search_text)

    def load_suppliers(self):
        self.comboBox_sort_suppliers.clear()
        self.comboBox_sort_suppliers.addItem("Все поставщики")
        try:
            suppliers = db.fetch_all("""
                SELECT supplier_name
                FROM suppliers
            """)
            for supplier in suppliers:
                self.comboBox_sort_suppliers.addItem(supplier["supplier_name"])
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))

    def logout(self):
        from modules.auth import AuthWindow
        self.window = AuthWindow()
        self.window.show()
        self.close()

    def show_orders(self):
        from modules.order import OrderWindow
        self.window = OrderWindow(self.role_name, self.user_fio)
        self.window.show()
        self.hide()
