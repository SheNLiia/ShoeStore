import pymysql
from PyQt6.QtCore import Qt

from modules.database import db
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic


class OrderWindow(QMainWindow):
    def __init__(self, role_name=None, user_fio=None, user_id=3):
        super().__init__()

        uic.loadUi("ui/order.ui", self)

        self.role_name = role_name
        self.user_fio = user_fio
        self.user_id = user_id

        if self.role_name == "Менеджер":
            self.pushButton_back.clicked.connect(self.back_to_manager)
            self.pushButton_add.hide()
        else:
            self.pushButton_back.clicked.connect(self.back_to_admin)
            self.pushButton_add.clicked.connect(self.add_order)

        self.load_orders()

    def load_orders(self):
        for i in reversed(range(self.verticalLayout_order.count())):
            self.verticalLayout_order.itemAt(i).widget().setParent(None)

        try:
            orders = db.fetch_all("""
                                  SELECT o.*, pp.full_address, os.status_name, p.article
                                  FROM orders o
                                           LEFT JOIN pickup_points pp ON pp.pickup_point_id = o.pickup_point_id
                                           LEFT JOIN order_statuses os ON os.status_id = o.status_id
                                           LEFT JOIN OrderItems oi ON oi.order_id = o.order_id
                                           LEFT JOIN Products p ON p.product_id = oi.product_id
                                  """)
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        for order in orders:
            widget = uic.loadUi("ui/widget_order.ui")

            widget.label_order_id.setText(f"Артикул заказа: {order['article']}")
            widget.label_order_status.setText(f"Статус заказа: {order['status_name']}")
            widget.label_delivery_address.setText(f"Адрес пункта выдачи: {order['full_address']}")
            widget.label_order_date.setText(f"Дата заказа: {order['order_date']}")

            widget.label_delivery_date.setText(f"Дата доставки: {order['delivery_date']}")

            if self.role_name == "Администратор":
                widget.mousePressEvent = lambda event, i=order: (
                    self.edit_order(i) if event.button() == Qt.MouseButton.RightButton else None)
                widget.mouseDoubleClickEvent = lambda event, i=order: self.delete_order(i)

            self.verticalLayout_order.addWidget(widget)

    def delete_order(self, order):
        order_id = order["order_id"]

        try:
            db.execute("DELETE FROM OrderItems WHERE order_id = %s", (order_id,))

            db.execute("DELETE FROM Orders WHERE order_id = %s", (order_id,))

        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
            return

        QMessageBox.information(self, "Успех", "Заказ удалён")
        self.load_orders()

    def add_order(self):
        form = uic.loadUi("ui/create_edit_order.ui")

        statuses = db.fetch_all("SELECT * FROM Order_statuses")

        for status in statuses:
            form.comboBox_status.addItem(status["status_name"], status["status_id"])

        if form.exec():
            article = form.lineEdit_article.text()
            full_address = form.lineEdit_full_address.text()
            order_date = form.dateEdit_order_date.date().toString("yyyy-MM-dd")
            delivery_date = form.dateEdit_delivery_date.date().toString("yyyy-MM-dd")

            if article == "" or full_address == "" or order_date == "" or delivery_date == "":
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return

            try:
                pickup_point = db.fetch_one("SELECT * FROM Pickup_points WHERE full_address = %s", (full_address,))

                if pickup_point:
                    pickup_point_id = pickup_point["pickup_point_id"]
                else:
                    pickup_point_id = db.execute("INSERT INTO Pickup_points (full_address) VALUES (%s)",
                                                 (full_address,))

                product = db.fetch_one("SELECT * FROM Products WHERE article = %s", (article,))

                if product:
                    product_id = product["product_id"]
                else:
                    QMessageBox.warning(self, "Ошибка", "Товар не найден")
                    return

                status_id = form.comboBox_status.currentData()

                order_id = db.execute("""
                                      INSERT INTO Orders (user_id, pickup_point_id, pickup_code, status_id, order_date,
                                                          delivery_date)
                                      VALUES (%s, %s, %s, %s, %s, %s)
                                      """, (self.user_id, pickup_point_id, "000", status_id, order_date, delivery_date))

                db.execute("""
                           INSERT INTO OrderItems (order_id, product_id, quantity, price)
                           VALUES (%s, %s, %s, %s)
                           """, (order_id, product_id, 1, product["price"]))

            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))
                return

            QMessageBox.information(self, "Успех", "Заказ добавлен")
            self.load_orders()

    def edit_order(self, order):
        order_id = order["order_id"]

        form = uic.loadUi("ui/create_edit_order.ui")

        statuses = db.fetch_all("SELECT status_name FROM Order_statuses")

        for status in statuses:
            form.comboBox_status.addItem(status["status_name"])

        order = db.fetch_one("""
                             SELECT o.*, pp.full_address, os.status_name, p.article
                             FROM Orders o
                                      LEFT JOIN Pickup_points pp ON pp.pickup_point_id = o.pickup_point_id
                                      LEFT JOIN Order_statuses os ON os.status_id = o.status_id
                                      LEFT JOIN OrderItems oi ON oi.order_id = o.order_id
                                      LEFT JOIN Products p ON p.product_id = oi.product_id
                             WHERE o.order_id = %s
                             """, (order_id,))

        form.lineEdit_article.setText(order["article"])
        form.comboBox_status.setCurrentText(order["status_name"])
        form.lineEdit_full_address.setText(order["full_address"])

        form.dateEdit_order_date.setDate(order["order_date"])
        form.dateEdit_delivery_date.setDate(order["delivery_date"])

        form.pushButton_cancel.clicked.connect(form.close)

        if form.exec():
            article = form.lineEdit_article.text()
            status = form.comboBox_status.currentText()
            full_address = form.lineEdit_full_address.text()
            order_date = form.dateEdit_order_date.date().toString("yyyy-MM-dd")
            delivery_date = form.dateEdit_delivery_date.date().toString("yyyy-MM-dd")

            try:
                pickup_point = db.fetch_one("SELECT * FROM Pickup_points WHERE full_address = %s", (full_address,))

                if pickup_point:
                    pickup_point_id = pickup_point["pickup_point_id"]
                else:
                    pickup_point_id = db.execute("INSERT INTO Pickup_points (full_address) VALUES (%s)",
                                                 (full_address,))

                status = db.fetch_one("SELECT * FROM Order_statuses WHERE status_name = %s", (status,))
                status_id = status["status_id"]

                product = db.fetch_one("SELECT * FROM Products WHERE article = %s", (article,))

                if not product:
                    QMessageBox.warning(self, "Ошибка", "Товар не найден")
                    return

                product_id = product["product_id"]

                db.execute("""
                           UPDATE Orders
                           SET pickup_point_id = %s,
                               status_id       = %s,
                               order_date      = %s,
                               delivery_date   = %s
                           WHERE order_id = %s
                           """, (pickup_point_id, status_id, order_date, delivery_date, order_id))

                db.execute("""
                           UPDATE OrderItems
                           SET product_id = %s,
                               price      = %s
                           WHERE order_id = %s
                           """, (product_id, product["price"], order_id))

            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка БД", str(e))
                return

            QMessageBox.information(self, "Успех", "Заказ изменён")
            self.load_orders()

    def back_to_manager(self):
        from modules.manager import ManagerWindow
        self.window = ManagerWindow(self.role_name, self.user_fio)
        self.window.show()
        self.close()

    def back_to_admin(self):
        from modules.admin import AdminWindow
        self.window = AdminWindow(self.role_name, self.user_fio)
        self.window.show()
        self.close()
