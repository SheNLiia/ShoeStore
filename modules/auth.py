import sys
import traceback
import pymysql
from modules.admin import AdminWindow
from modules.client import ClientWindow
from modules.database import db
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic
from modules.manager import ManagerWindow


class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("ui/auth.ui", self)

        self.pushButton_enter.clicked.connect(self.check_user)
        self.pushButton_enter_guest.clicked.connect(self.login_guest)

    def check_user(self):
        username = self.lineEdit_login.text()
        password_hash = self.lineEdit_password.text()

        if not username or not password_hash:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            user = db.fetch_one("""
                                SELECT u.*, r.role_name, r.role_id
                                FROM users u
                                         JOIN roles r ON r.role_id = u.role_id
                                WHERE username = %s
                                  AND password_hash = %s
                                """, (username, password_hash))
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Ошибка БД: ", str(e))
            return

        if not user:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return

        role_id = user['role_id']
        user_id = user['user_id']
        role_name = user['role_name']
        user_fio = f"{user['surname']} {user['name']} {user['patronymic']}"

        # Открываю окно в зависимости от роли пользователя
        if role_id == 1:
            self.window = ClientWindow(role_name, user_fio, user_id)
        elif role_id == 2:
            self.window = ManagerWindow(role_name, user_fio)
        elif role_id == 3:
            self.window = AdminWindow(role_name, user_fio)

        self.window.show()
        self.close()

        QMessageBox.information(self, "Успех", f"Добро пожаловать {role_name}!")

    def login_guest(self):
        self.window = ClientWindow(None)
        self.window.show()
        self.close()

        QMessageBox.information(self, "Успех", "Добро пожаловать гость!")

    def a(b, c, d):
        traceback.print_exception(b, c, d)

    sys.excepthook = a
