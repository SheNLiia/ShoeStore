import pymysql
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from modules.database import db
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog
import shutil
import os


class AdminWindow(QMainWindow):
    def __init__(self, role_name=None, user_fio=None):
        super().__init__()

        uic.loadUi("ui/admin.ui", self)

        self.role_name = role_name
        self.user_fio = user_fio

        self.label_role.setText(f"{role_name}: {user_fio}")

        self.pushButton_exit.clicked.connect(self.logout)
        self.comboBox_sort.currentTextChanged.connect(self.sort_menu)
        self.lineEdit_search.textChanged.connect(self.sort_menu)
        self.comboBox_sort_suppliers.currentTextChanged.connect(self.sort_menu)
        self.pushButton_order.clicked.connect(self.show_orders)
        self.pushButton_add.clicked.connect(self.add_item)

        self.load_menu()
        self.load_suppliers()

    def load_menu(self, text="DESC", supplier="Все поставщики", search_text=""):
        # Очищаю текущий список товаров перед повторной загрузкой
        for i in reversed(range(self.verticalLayout_menu.count())):
            self.verticalLayout_menu.itemAt(i).widget().setParent(None)

        try:
            if supplier == "Все поставщики":
                # Поиск выполняется одновременно по названию, описанию, категории, производителю и поставщику
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

            widget.mouseDoubleClickEvent = lambda event, i=item: self.delete_item(i)
            widget.mousePressEvent = lambda event, i=item: (
                self.edit_item(i) if event.button() == Qt.MouseButton.RightButton else None)

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

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото",
            "C:/Users/Emily/Downloads/Telegram Desktop",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not file_path:
            return

        # Создаю папку images, если она отсутствует
        os.makedirs("images", exist_ok=True)

        file_name = os.path.basename(file_path)
        new_path = os.path.join("images", file_name)

        # Копирую выбранное изображение в папку проекта
        if os.path.abspath(file_path) != os.path.abspath(new_path):
            shutil.copy(file_path, new_path)

        self.image_path = new_path

        pixmap = QPixmap(new_path)
        pixmap = pixmap.scaled(300, 200)

        self.form.label_photo.setPixmap(pixmap)

    def delete_item(self, item):
        product_id = item["product_id"]

        order_item = db.fetch_one(
            "SELECT * FROM OrderItems WHERE product_id = %s",
            (product_id,)
        )

        # Запрещаю удаление товара, если он присутствует в заказах
        if order_item:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нельзя удалить товар, так как он присутствует в заказе"
            )
            return

        try:
            db.execute(
                "DELETE FROM Products WHERE product_id = %s",
                (product_id,)
            )
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
            return

        QMessageBox.information(self, "Успех", "Товар удалён")
        self.sort_menu()

    def edit_item(self, item):
        form = uic.loadUi("ui/create_edit_item.ui")

        product_id = item["product_id"]

        item = db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (product_id,))

        form.lineEdit_product_id.setText(str(item["product_id"]))
        form.lineEdit_product_id.setReadOnly(True)

        self.form = form
        self.image_path = item["image_path"]
        self.old_image_path = item["image_path"]

        form.pushButton_choose_photo.clicked.connect(self.choose_image)

        categories = db.fetch_all("SELECT * FROM Categories")
        manufacturers = db.fetch_all("SELECT * FROM Manufacturers")

        for category in categories:
            form.comboBox_category_name.addItem(category["category_name"], category["category_id"])

        for manufacturer in manufacturers:
            form.comboBox_manufacturer_name.addItem(manufacturer["manufacturer_name"], manufacturer["manufacturer_id"])

        form.comboBox_category_name.setCurrentIndex(form.comboBox_category_name.findData(item["category_id"]))
        form.comboBox_manufacturer_name.setCurrentIndex(
            form.comboBox_manufacturer_name.findData(item["manufacturer_id"]))

        form.lineEdit_product_name.setText(item["product_name"])
        form.lineEdit_price.setText(str(item["price"]))
        form.lineEdit_unit.setText(item["unit"])
        form.lineEdit_stock_quantity.setText(str(item["stock_quantity"]))
        form.lineEdit_discount_percentage.setText(str(item["discount_percentage"]))
        form.lineEdit_description.setText(item["description"])
        form.lineEdit_article.setText(item["article"])

        supplier = db.fetch_one(
            "SELECT supplier_name FROM Suppliers WHERE supplier_id = %s",
            (item["supplier_id"],)
        )

        form.lineEdit_supplier_name.setText(supplier["supplier_name"])

        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaled(300, 200)

        form.label_photo.setPixmap(pixmap)

        if form.exec():
            product_name = form.lineEdit_product_name.text()
            price = form.lineEdit_price.text()
            unit = form.lineEdit_unit.text()
            stock_quantity = form.lineEdit_stock_quantity.text()
            discount_percentage = form.lineEdit_discount_percentage.text()
            description = form.lineEdit_description.text()
            article = form.lineEdit_article.text()
            supplier = form.lineEdit_supplier_name.text()

            if (product_name == "" or price == "" or unit == "" or stock_quantity == ""
                    or discount_percentage == "" or description == ""
                    or article == "" or supplier == ""):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return

            try:
                category_id = form.comboBox_category_name.currentData()
                manufacturer_id = form.comboBox_manufacturer_name.currentData()

                supplier_data = db.fetch_one(
                    "SELECT * FROM Suppliers WHERE supplier_name = %s",
                    (supplier,)
                )

                if supplier_data:
                    supplier_id = supplier_data["supplier_id"]
                else:
                    supplier_id = db.execute(
                        "INSERT INTO Suppliers (supplier_name) VALUES (%s)",
                        (supplier,)
                    )

                db.execute("""
                           UPDATE Products
                           SET article=%s,
                               product_name=%s,
                               category_id=%s,
                               description=%s,
                               manufacturer_id=%s,
                               supplier_id=%s,
                               price=%s,
                               unit=%s,
                               stock_quantity=%s,
                               discount_percentage=%s,
                               image_path=%s
                           WHERE product_id = %s
                           """, (article, product_name, category_id, description, manufacturer_id, supplier_id,
                                 price, unit, stock_quantity, discount_percentage, self.image_path, product_id
                                 ))

                # Удаляю старое изображение после замены на новое
                if (self.old_image_path != self.image_path and os.path.exists(self.old_image_path)):
                    os.remove(self.old_image_path)

            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))
                return

            QMessageBox.information(self, "Успех", "Товар изменён")

            form.close()
            self.sort_menu()

    def add_item(self):
        form = uic.loadUi("ui/create_edit_item.ui")

        form.lineEdit_product_id.hide()

        self.form = form
        self.image_path = "images/picture.png"

        form.pushButton_choose_photo.clicked.connect(self.choose_image)

        categories = db.fetch_all("SELECT * FROM Categories")
        manufacturers = db.fetch_all("SELECT * FROM Manufacturers")

        for category in categories:
            form.comboBox_category_name.addItem(category["category_name"], category["category_id"])

        for manufacturer in manufacturers:
            form.comboBox_manufacturer_name.addItem(manufacturer["manufacturer_name"], manufacturer["manufacturer_id"])

        if form.exec():
            product_name = form.lineEdit_product_name.text()
            price = form.lineEdit_price.text()
            unit = form.lineEdit_unit.text()
            stock_quantity = form.lineEdit_stock_quantity.text()
            discount_percentage = form.lineEdit_discount_percentage.text()
            description = form.lineEdit_description.text()
            article = form.lineEdit_article.text()
            supplier_name = form.lineEdit_supplier_name.text()

            if (product_name == "" or price == "" or unit == "" or stock_quantity == "" or discount_percentage == ""
                    or description == "" or article == "" or supplier_name == ""):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return

            try:
                category_id = form.comboBox_category_name.currentData()
                manufacturer_id = form.comboBox_manufacturer_name.currentData()

                supplier = db.fetch_one("SELECT * FROM Suppliers WHERE supplier_name = %s", (supplier_name,))

                if supplier:
                    supplier_id = supplier['supplier_id']
                else:
                    supplier_id = db.execute("INSERT INTO Suppliers (supplier_name) VALUES (%s)", (supplier_name,))

                product = db.fetch_one("SELECT * FROM Products WHERE article = %s", (article,))

                if product:
                    QMessageBox.warning(self, "Ошибка", "Такой артикул товара уже существует. Введите другой.")
                    return

                db.execute("""
                           INSERT INTO Products (article, product_name, category_id, description, manufacturer_id,
                                                 supplier_id, price, unit, stock_quantity, discount_percentage,
                                                 image_path)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (article, product_name, category_id, description, manufacturer_id,
                                 supplier_id, price, unit, stock_quantity, discount_percentage, self.image_path))

            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))
                return

            QMessageBox.information(self, "Успех", "Товар добавлен")
            self.sort_menu()
