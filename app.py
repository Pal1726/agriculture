from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rathi@123",
        database="faker"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sellers')
def sellers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Seller")
    sellers = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('sellers.html', sellers_i=sellers)

@app.route('/buyers')
def buyers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Buyer")
    buyers = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('buyers.html', buyers=buyers)

@app.route('/products')
def products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('products.html', products=products)

# Cart page with specific fields
@app.route('/cart')
def cart():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            Cart.cart_id AS serial_number,
            Product.product_title AS product_name,
            Product.product_mrp AS price,
            Cart.quantity,
            (Product.product_mrp * Cart.quantity) AS subtotal
        FROM 
            Cart
        JOIN 
            Product ON Cart.product_id = Product.product_id
    """)
    cart_items = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/order')
def order():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # SQL query to fetch the necessary details for the order
    cursor.execute("""
        SELECT 
            o.order_id AS serial_no, 
            Buyer.name AS buyer_name,
            GROUP_CONCAT(p.product_title SEPARATOR ', ') AS product_titles, 
            CONCAT(a.street, ', ', a.city, ', ', a.region, ', ', a.pincode, ', ', a.country) AS delivery_address,
            o.total_amount AS subtotal, 
            pay.payment_method
        FROM 
            Orders o
            JOIN Buyer ON o.buyer_id = Buyer.buyer_id
            JOIN OrderItem oi ON o.order_id = oi.order_id
            JOIN Product p ON oi.product_id = p.product_id
            JOIN Address a ON Buyer.address_id = a.address_id
            JOIN Payment pay ON o.order_id = pay.order_id
        GROUP BY 
            o.order_id, Buyer.name, delivery_address, o.total_amount, pay.payment_method
    """)
    
    order_details = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('order.html', order_details=order_details)

@app.route('/transaction')
def transaction():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            s.name AS seller_name,
            b.name As buyer_name,
            b.phone1 AS phone_number, 
            CONCAT(a.street, ', ', a.city, ', ', a.region, ', ', a.pincode, ', ', a.country) AS delivery_address,
            p.product_title, 
            oi.quantity, 
            oi.total_price AS amount,  
            pay.payment_method AS payment_mode
        FROM 
            Transaction t
            JOIN Orders o ON t.order_id = o.order_id
            JOIN Buyer b ON t.buyer_id = b.buyer_id
            JOIN Seller s ON t.seller_id = s.seller_id
            JOIN OrderItem oi ON o.order_id = oi.order_id
            JOIN Product p ON oi.product_id = p.product_id
            JOIN Address a ON b.address_id = a.address_id
            JOIN Payment pay ON o.order_id = pay.order_id
        GROUP BY
            seller_name,buyer_name,phone_number,delivery_address,p.product_title,oi.quantity,oi.total_price,payment_mode

    """)
    
    transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('transaction_buyer.html', transactions=transactions)






if __name__ == '__main__':
    app.run(debug=True)