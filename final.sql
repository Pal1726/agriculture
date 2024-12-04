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
    delivery_available TINYINT(1)NOT NULL,
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



CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT,
    total_amount DECIMAL(10, 2) DEFAULT NULL,
    order_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id),
    
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

ALTER TABLE Cart
ADD UNIQUE (buyer_id, product_id);

CREATE TABLE IF NOT EXISTS BuyerAddress (
    buyer_address_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    address_id INT NOT NULL,
    FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES Address(address_id) ON DELETE CASCADE
);
ALTER TABLE Transaction
ADD UNIQUE (order_id,buyer_id, seller_id);






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


