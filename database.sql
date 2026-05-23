CREATE DATABASE IF NOT EXISTS ShoeStore;
USE ShoeStore;

-- 1. Таблица ролей пользователей
CREATE TABLE Roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO Roles (role_name)
VALUES
('Клиент'),
('Менеджер'),
('Администратор');

-- 2.Таблица пользователей
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    surname VARCHAR(50),
    patronymic VARCHAR(50),
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id)
);

INSERT INTO Users
(name, surname, patronymic, username, password_hash, role_id)
VALUES
('Весения', 'Никифорова', 'Николаевна', '94d5ous@gmail.com', 'uzWC67', 3),
('Вения', 'Никифова', 'Николаевна', '3', '3', 3),
('Руслан', 'Сазонов', 'Германович', 'uth4iz@mail.com', '2L6KZG', 3),
('Серафим', 'Одинцов', 'Артёмович', 'yzls62@outlook.com', 'JlFRCZ', 3),
('Михаил', 'Степанов', 'Артёмович', '1diph5e@tutanota.com', '8ntwUp', 2),
('Майкал', 'Степанов', 'Петрович', '2', '2', 2),
('Петр', 'Ворсин', 'Евгеньевич', 'tjde7c@yahoo.com', 'YOyhfR', 2),
('Валерия', 'Кузнецова', 'Ивановна', 'user1@mail.com', 'pass1', 1),
('Алла', 'Кузнецова', 'Александровна', '1', '1', 1),
('Анна', 'Соколова', 'Петровна', 'user2@mail.com', 'pass2', 1),
('Илья', 'Миронов', 'Сергеевич', 'user3@mail.com', 'pass3', 1),
('Егор', 'Федоров', 'Алексеевич', 'user4@mail.com', 'pass4', 1),
('Мария', 'Орлова', 'Викторовна', 'user5@mail.com', 'pass5', 1);

-- 3. Таблица производителей обуви
CREATE TABLE Manufacturers (
    manufacturer_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO Manufacturers (manufacturer_name)
VALUES
('Kari'),
('Marco Tozzi'),
('Рос'),
('Rieker');

-- 4. Таблица поставщиков обуви
CREATE TABLE Suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name VARCHAR(100)
);

INSERT INTO Suppliers (supplier_name)
VALUES
('Kari'),
('Обувь для вас');

-- 5.Категории обуви
CREATE TABLE Categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO Categories (category_name)
VALUES
('Женская обувь'),
('Мужская обувь');

-- 6. Таблица товаров (обувь)
CREATE TABLE Products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    article VARCHAR(50) UNIQUE,
    product_name VARCHAR(100) NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    description TEXT,
    manufacturer_id INT,
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturers(manufacturer_id),
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id),
    price DECIMAL(10,2),
    unit VARCHAR(20),
    stock_quantity INT,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    image_path VARCHAR(255) NOT NULL
);

INSERT INTO Products
(article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit, stock_quantity, discount_percentage, image_path)
VALUES
('А112Т4', 'Ботинки', 1, 'Женские Ботинки демисезонные kari', 1, 1, 4990, 'шт.', 0, 3, 'images/1.jpg'),
('F635R4', 'Ботинки', 1, 'Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый', 2, 2, 3244, 'шт.', 13, 0, 'images/5.jpg'),
('H782T5', 'Туфли', 2, 'Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет черный', 1, 1, 4499, 'шт.', 5, 4, 'images/4.jpg'),
('G783F5', 'Ботинки', 2, 'Мужские ботинки Рос-Обувь кожаные с натуральным мехом', 3, 1, 5900, 'шт.', 8, 2, 'images/2.jpg'),
('J384T6', 'Ботинки', 2, 'Полуботинки мужские Rieker', 4, 2, 3800, 'шт.', 16, 20, 'images/3.jpg');

-- 7. Таблица пунктов выдачи
CREATE TABLE Pickup_points (
    pickup_point_id INT PRIMARY KEY AUTO_INCREMENT,
    full_address VARCHAR(255)
);

INSERT INTO Pickup_points (pickup_point_id, full_address)
VALUES
(11, 'г. Лесной, ул. Центральная, 11'),
(15, 'г. Лесной, ул. Садовая, 15'),
(19, 'г. Лесной, ул. Молодежная, 19');

-- 8. Таблица статусов заказов
CREATE TABLE Order_statuses (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_name VARCHAR(50) UNIQUE
);

INSERT INTO Order_statuses (status_name)
VALUES
('Завершен'),
('Новый');

-- 9.Таблица заказов
CREATE TABLE Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    pickup_point_id INT,
    FOREIGN KEY (pickup_point_id) REFERENCES Pickup_points(pickup_point_id),
    pickup_code VARCHAR(20),
    status_id INT,
    FOREIGN KEY (status_id) REFERENCES Order_statuses(status_id),
    order_date DATE DEFAULT (CURRENT_DATE),
    delivery_date DATE DEFAULT (CURRENT_DATE)
);

INSERT INTO Orders
(order_id, user_id, pickup_point_id, pickup_code, status_id, order_date, delivery_date)
VALUES
(1, 4, 11, '901', 1, '2025-02-27', '2025-04-20'),
(2, 1, 11, '902', 1, '2022-09-28', '2025-04-21'),
(3, 2, 15, '903', 1, '2025-03-21', '2025-04-22'),
(4, 3, 11, '904', 1, '2025-02-20', '2025-04-23'),
(5, 4, 15, '905', 1, '2025-03-17', '2025-04-24'),
(6, 1, 15, '906', 1, '2025-03-01', '2025-04-25'),
(7, 2, 19, '907', 1, '2025-02-28', '2025-04-26'),
(8, 3, 19, '908', 2, '2025-03-31', '2025-04-27'),
(9, 4, 19, '909', 2, '2025-04-02', '2025-04-28'),
(10, 1, 11, '910', 2, '2025-04-05', '2025-04-29');

-- 10. Таблица деталей заказа
CREATE TABLE OrderItems (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

INSERT INTO OrderItems
(order_id, product_id, quantity, price)
VALUES
(1, 1, 2, 4990),
(1, 2, 2, 3244),
(2, 3, 1, 4499),
(2, 4, 1, 5900),
(3, 5, 10, 3800),
(3, 1, 10, 4990),
(4, 2, 5, 3244),
(4, 3, 4, 4499),
(5, 1, 2, 4990),
(5, 2, 2, 3244),
(6, 3, 1, 4499),
(6, 4, 1, 5900),
(7, 5, 10, 3800),
(7, 1, 10, 4990),
(8, 2, 5, 3244),
(8, 3, 4, 4499),
(9, 4, 5, 5900),
(9, 5, 1, 3800),
(10, 1, 2, 4990),
(10, 2, 2, 3244);