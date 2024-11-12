CREATE TABLE IF NOT EXISTS Address (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    pincode VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS ProductCategory (
    product_category_id INT AUTO_INCREMENT PRIMARY KEY,
    product_category_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Seller (
    seller_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone1 VARCHAR(20) NOT NULL,
    phone2 VARCHAR(20) DEFAULT NULL,
    gst_number VARCHAR(15) DEFAULT NULL,  -- Adding GST number
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE IF NOT EXISTS Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_title VARCHAR(255) NOT NULL,
    product_stock DECIMAL(10, 2) NOT NULL,
    product_category_id INT,
    product_expiry DATE,
    product_image VARCHAR(255),
    product_mrp DECIMAL(10, 2) NOT NULL,
    product_description TEXT,
    d,
    seller_id INT,
    FOREIGN KEY (product_category_id) REFERENCES ProductCategory(product_category_id),
    FOREIGN KEY (seller_id) REFERENCES Seller(seller_id)
);

CREATE TABLE IF NOT EXISTS Buyer (
    buyer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone1 VARCHAR(20) NOT NULL,
    phone2 VARCHAR(20) DEFAULT NULL,
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE IF NOT EXISTS Cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT,
    product_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE IF NOT EXISTS Shipping (
    shipping_id INT AUTO_INCREMENT PRIMARY KEY,
    address_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    tracking_number VARCHAR(50),
    delivery_date DATETIME NOT NULL,
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT,
    total_amount DECIMAL(10, 2) DEFAULT NULL,
    order_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    shipping_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id),
    FOREIGN KEY (shipping_id) REFERENCES Shipping(shipping_id)
);


CREATE TABLE IF NOT EXISTS OrderItem (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) DEFAULT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE IF NOT EXISTS Transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    buyer_id INT,
    seller_id INT,
    amount DECIMAL(10, 2) DEFAULT NULL,
    transaction_date DATETIME NOT NULL,
    transaction_status VARCHAR(50) NOT NULL DEFAULT 'Completed',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id),
    FOREIGN KEY (seller_id) REFERENCES Seller(seller_id)
);

CREATE TABLE IF NOT EXISTS Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);


INSERT INTO Address (street, city, region, pincode, country) VALUES
('123 Green Lane', 'Mumbai', 'Maharashtra', '400001', 'India'),
('456 Blue Street', 'Delhi', 'Delhi', '110001', 'India'),
('789 Red Road', 'Bangalore', 'Karnataka', '560001', 'India'),
('321 Yellow Boulevard', 'Hyderabad', 'Telangana', '500001', 'India'),
('654 Orange Avenue', 'Chennai', 'Tamil Nadu', '600001', 'India');


INSERT INTO ProductCategory (product_category_name) VALUES
('Fruits'),
('Vegetables'),
('Crops'),
('Seeds'),
('Fertilizer'),
('Pesticides');

INSERT INTO Seller (name, username, email, password, phone1, phone2, gst_number, address_id) VALUES
('John Doe', 'johndoe', 'john@example.com', 'password1', '9876543210', '9123456780', 'GST12345', 1),
('Jane Smith', 'janesmith', 'jane@example.com', 'password2', '8765432109', '9234567890', 'GST67890', 2),
('Raj Patel', 'rajpatel', 'raj@example.com', 'password3', '7654321098', NULL, 'GST11223', 3),
('Anita Sharma', 'anitasharma', 'anita@example.com', 'password4', '6543210987', '9345678901', 'GST44556', 4),
('Arjun Reddy', 'arjunreddy', 'arjun@example.com', 'password5', '5432109876', '9456789012', 'GST77889', 5);

INSERT INTO Product (product_title, product_stock, product_category_id, product_expiry, product_image, product_mrp, product_description, delivery_available, seller_id) VALUES
('Mango', 100, 1, '2025-01-01', 'mango.jpg', 150.00, 'Fresh and juicy mangoes.', TRUE, 1),
('Banana', 150, 1, '2025-01-01', 'banana.jpg', 50.00, 'Ripe bananas.', TRUE, 2),
('Tomato', 200, 2, '2025-01-01', 'tomato.jpg', 30.00, 'Fresh tomatoes.', TRUE, 3),
('Carrot', 120, 2, '2025-01-01', 'carrot.jpg', 40.00, 'Crunchy carrots.', TRUE, 4),
('Wheat', 300, 3, '2025-01-01', 'wheat.jpg', 25.00, 'Organic wheat.', TRUE, 5),
('Corn', 250, 3, '2025-01-01', 'corn.jpg', 20.00, 'Sweet corn.', TRUE, 1),
('Sunflower Seeds', 500, 4, '2025-01-01', 'sunflower_seeds.jpg', 100.00, 'High-quality sunflower seeds.', TRUE, 1),
('Fertilizer Mix', 300, 5, '2025-01-01', 'fertilizer.jpg', 200.00, 'Nutrient-rich fertilizer mix.', TRUE, 2),
('Pesticide Spray', 150, 6, '2025-01-01', 'pesticide.jpg', 300.00, 'Effective pesticide spray.', TRUE, 3);

INSERT INTO Buyer (name, username, email, password, phone1, phone2, address_id) VALUES
('Rahul Mehta', 'rahulmehta', 'rahul@example.com', 'password1', '9871234567', '9123456789', 1),
('Sneha Iyer', 'snehaiyer', 'sneha@example.com', 'password2', '8762345678', '9234567890', 2),
('Vikram Saini', 'vikramsaini', 'vikram@example.com', 'password3', '7653456789', NULL, 3),
('Priya Verma', 'priyaverma', 'priya@example.com', 'password4', '6544567890', '9345678901', 4),
('Deepak Joshi', 'deepakjoshi', 'deepak@example.com', 'password5', '5435678901', '9456789012', 5);

INSERT INTO Cart (buyer_id, product_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1),
(2, 3, 3),
(3, 4, 5),
(4, 5, 1);

INSERT INTO Shipping (address_id, status, tracking_number, delivery_date) VALUES
(1, 'Pending', 'TRK123456', '2024-11-01 10:00:00'),
(2, 'Shipped', 'TRK654321', '2024-10-30 10:00:00'),
(3, 'Delivered', NULL, '2024-10-25 10:00:00'),
(4, 'Pending', NULL, '2024-11-05 10:00:00');


INSERT INTO Orders (buyer_id, order_status, shipping_id) VALUES
(1, 'Pending', 1),
(2, 'Pending', 2),
(3, 'Delivered', 3),
(4, 'Pending', 4);

INSERT INTO OrderItem (order_id, product_id, quantity) VALUES
(1, 1, 2),  
(1, 2, 1), 
(2, 3, 3),  
(3, 4, 5),  
(4, 5, 1);  

INSERT INTO Transaction (order_id, buyer_id, seller_id, transaction_date, transaction_status) VALUES
(1, 1, 1, '2024-10-20 10:00:00', 'Completed'),
(2, 2, 2, '2024-10-21 10:00:00', 'Completed'),
(3, 3, 3, '2024-10-22 10:00:00', 'Completed'),
(4, 4, 4, '2024-10-23 10:00:00', 'Completed');


INSERT INTO Payment (order_id, payment_method, payment_status) VALUES
(1, 'Credit Card', 'Completed'),
(2, 'Debit Card', 'Completed'),
(3, 'Net Banking', 'Completed'),
(4, 'UPI', 'Pending');


UPDATE OrderItem AS oi
JOIN Product AS p ON oi.product_id = p.product_id
SET oi.total_price = oi.quantity * p.product_mrp;


UPDATE Orders AS o
SET total_amount = (
    SELECT SUM(oi.total_price)
    FROM OrderItem AS oi
    WHERE oi.order_id = o.order_id
);


UPDATE Transaction AS t
JOIN Orders AS o ON t.order_id = o.order_id
SET t.amount = o.total_amount;


