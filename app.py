from math import ceil
from flask import Flask, render_template,request
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
    page=request.args.get('page',1,type=int)
    per_page=10
    offset=(page-1)*per_page   #starting point for current page
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Seller")  #total no of rows in seller table
    total=cursor.fetchone()['total']

    cursor.execute("SELECT * FROM Seller LIMIT %s OFFSET %s",(per_page,offset))
    sellers = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)

    return render_template('sellers.html', sellers_i=sellers,page=page, total_pages=total_pages)

@app.route('/buyers')
def buyers():
    page=request.args.get('page',1,type=int)
    per_page=10
    offset=(page-1)*per_page  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Buyer")  
    total=cursor.fetchone()['total']

    cursor.execute("SELECT * FROM Buyer LIMIT %s OFFSET %s",(per_page,offset))
    buyers = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)

    return render_template('buyers.html', buyers=buyers,page=page, total_pages=total_pages)

@app.route('/products')
def products():
    page=request.args.get('page',1,type=int)
    per_page=10
    offset=(page-1)*per_page  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Product")  
    total=cursor.fetchone()['total']

    cursor.execute("SELECT * FROM Product LIMIT %s OFFSET %s",(per_page,offset))
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)

    return render_template('products.html', products=products,page=page, total_pages=total_pages)

# Cart page with specific fields
@app.route('/cart')
def cart():
    page=request.args.get('page',1,type=int)
    per_page=10
    offset=(page-1)*per_page  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Cart")  
    total=cursor.fetchone()['total']

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
            Product ON Cart.product_id = Product.product_id LIMIT %s OFFSET %s""",(per_page,offset))
    
    cart_items = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)
    return render_template('cart.html', cart_items=cart_items,page=page, total_pages=total_pages)

@app.route('/order')
def order():
    page=request.args.get('page',1,type=int)
    per_page=10
    offset=(page-1)*per_page  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # cursor.execute("SELECT COUNT(*) AS total from Orders")  
    # total=cursor.fetchone()['total']
    cursor.execute("SELECT COUNT( o.order_id) AS total FROM Orders o")  

    total = cursor.fetchone()['total']
    print("total",total)
    
    # SQL query to fetch the necessary details for the order
    cursor.execute("""
        SELECT 
            o.order_id AS serial_no, 
            Buyer.name AS buyer_name,
            p.product_title, 
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
            o.order_id, Buyer.name,p.product_title, delivery_address, o.total_amount, pay.payment_method 
        ORDER BY
            o.order_id ASC
            LIMIT %s OFFSET %s""",(per_page,offset))
    
    
    order_details = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)
    return render_template('order.html', order_details=order_details,page=page, total_pages=total_pages)

@app.route('/transaction')
def transaction():
    page=request.args.get('page',1,type=int)
    per_page=10
    offset=(page-1)*per_page  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Transaction")  
    total=cursor.fetchone()['total']
    
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
            seller_name,buyer_name,phone_number,delivery_address,p.product_title,oi.quantity,oi.total_price,payment_mode LIMIT %s OFFSET %s""",(per_page,offset))

 
    
    transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)
    return render_template('transaction_buyer.html', transactions=transactions,page=page, total_pages=total_pages)






if __name__ == '__main__':
    app.run(debug=True)


 

