
from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
import os
from werkzeug.security import check_password_hash, generate_password_hash
from math import ceil
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rathi@123",
        database="faker"
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to access this page.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                flash("You don't have permission to access this page.")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.after_request
def add_header(response):
    # Disable caching of all responses
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'  # Use '0' for better compatibility than '-1'
    return response


@app.route('/')
def home():
    # Check if the user is already logged in
    if 'user_id' in session and 'role' in session:
        if session['role'] == 'buyer':
            return redirect(url_for('buyer_dashboard'))  
        elif session['role'] == 'seller':
            return redirect(url_for('my_products'))  
    return render_template('index.html') 

# @app.route('/role_selection', methods=['POST'])
# def role_selection():
#     role = request.form['role']
#     if role == 'buyer':
#         return redirect(url_for('buyer_login'))
#     elif role == 'seller':
#         return redirect(url_for('seller_login'))




@app.route('/index')

def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html') 
    
@app.route('/buyer_login', methods=['GET', 'POST'])
def buyer_login():
    if 'user_id' in session and session.get('role') == 'buyer':
        return redirect(url_for('buyer_dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Buyer WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['buyer_id']  
            session['role'] = 'buyer'
            # print(session)
            flash("Login successful!","success")
            return redirect(url_for('buyer_dashboard'))
        else:
            flash("Invalid credentials!","error")
            return redirect(url_for('buyer_login'))
    
    return render_template('buyer_login.html')

@app.route('/seller_login', methods=['GET', 'POST'])
def seller_login():
    if 'user_id' in session and session.get('role') == 'seller':
        return redirect(url_for('add_product'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Seller WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['seller_id'] 
            session['role'] = 'seller'
            flash("Login successful!", "success")  
            return redirect(url_for('my_products'))
        else:
            flash("Invalid credentials!", "error")  
            return redirect(url_for('seller_login'))
    
    return render_template('seller_login.html')


@app.route('/buyer_signup', methods=['GET', 'POST'])
def buyer_signup():
    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone1 = request.form['phone1']
        phone2 = request.form.get('phone2')


        # Hash the password before saving to database
        hashed_password = generate_password_hash(password)

        # Connect to the database and insert buyer data
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Buyer (name, username, email, password, phone1, phone2)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, username, email, hashed_password, phone1, phone2))
            connection.commit()
            flash("Signup successful! You can now log in.","success")
            return redirect(url_for('buyer_login'))

        except mysql.connector.IntegrityError:
            flash("Username or email already exists. Please try again.","error")
            return redirect(url_for('buyer_signup'))

        finally:
            cursor.close()
            connection.close()

   
    return render_template('buyer_signup.html')


@app.route('/seller_signup', methods=['GET', 'POST'])
def seller_signup():
    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone1 = request.form['phone1']
        phone2 = request.form.get('phone2')
        gst = request.form['GST']

        # Address Fields
        street = request.form['street']
        city = request.form['city']
        region = request.form.get('region')
        pincode = request.form['pincode']
        country = request.form['country']

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Database Operations
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Insert into Address table first
            cursor.execute("""
                INSERT INTO Address (street, city, region, pincode, country)
                VALUES (%s, %s, %s, %s, %s)
            """, (street, city, region, pincode, country))
            address_id = cursor.lastrowid  # Get the auto-generated address_id

            # Insert into Seller table with the generated address_id
            cursor.execute("""
                INSERT INTO Seller (name, username, email, password, phone1, phone2, gst_number, address_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, username, email, hashed_password, phone1, phone2, gst, address_id))
            connection.commit()

            flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('seller_login'))

        except mysql.connector.IntegrityError:
            flash("Username or email already exists. Please try again.", "error")
            return redirect(url_for('seller_signup'))

        finally:
            cursor.close()
            connection.close()

    return render_template('seller_signup.html')

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def add_product():
    if request.method == 'POST':
        
        title = request.form['title']
        stock = request.form['stock']
        category_id = request.form['category']
        
        expiry = request.form.get('expiry')
        mrp = request.form['mrp']
        description = request.form.get('description')
        
        delivery = request.form['delivery']
       
        image = request.files['image']
        image_filename = image.filename
        if image:
            image.save(os.path.join('static/uploads', image_filename))
        seller_id = session.get('user_id') 
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Product 
            (product_title, product_stock, product_category_id, product_expiry, product_image, product_mrp, product_description, delivery_available,seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, stock, category_id, expiry, image_filename, mrp, description, delivery,seller_id))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("Product added successfully!")
        return redirect(url_for('my_products'))

    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ProductCategory")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('add_product.html', categories=categories)

@app.route('/my_products')
@login_required
@role_required('seller')
def my_products():
    # Get current page number, default is 1
    page = request.args.get('page', 1, type=int)
    per_page = 6  
    offset = (page - 1) * per_page

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query to get the total count of products for the seller
    count_query = """
        SELECT COUNT(*) 
        FROM Product
        WHERE seller_id = %s
    """
    seller_id = session.get('user_id')  
    cursor.execute(count_query, (seller_id,))
    total_products = cursor.fetchone()[0]  
    total_pages = ceil(total_products / per_page)  

    # Query to get the products for the current page
    product_query = """
        SELECT product_id, product_title, product_mrp, product_image 
        FROM Product
        WHERE seller_id = %s
        LIMIT %s OFFSET %s
    """
    cursor.execute(product_query, (seller_id, per_page, offset))
    products = cursor.fetchall()

    
    cursor.close()
    connection.close()

    
    return render_template('my_products.html',products=products,current_page=page, total_pages=total_pages )



@app.route('/product_details/<int:product_id>')
@login_required
@role_required('seller')
def product_details(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    product_query = """
        SELECT product_id, product_title, product_mrp, product_image, 
               product_description, product_stock, 
               delivery_available
        FROM Product
        WHERE product_id = %s AND seller_id = %s
    """
    seller_id = session.get('user_id')  # Ensure the product belongs to the logged-in seller
    cursor.execute(product_query, (product_id, seller_id))
    product = cursor.fetchone()

    cursor.close()
    connection.close()
    if not product:
        flash("Product not found or you don't have permission to view this product.", "danger")
        return redirect(url_for('my_products'))
    return render_template('product_details.html', product=product)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def edit_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Fetch updated details from the form
        title = request.form['title']
        stock = request.form['stock']
        category_id = request.form['category']
        expiry = request.form.get('expiry')
        mrp = request.form['mrp']
        description = request.form.get('description')
        delivery = request.form['delivery']
        
        # Handle image upload if provided
        image = request.files['image']
        seller_id = session.get('user_id')  # Ensure the seller is updating their own product
        
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join('static/uploads', image_filename))
            # Update with a new image
            cursor.execute("""
                UPDATE Product
                SET product_title = %s, product_stock = %s, product_category_id = %s,
                    product_expiry = %s, product_image = %s, product_mrp = %s,
                    product_description = %s, delivery_available = %s
                WHERE product_id = %s AND seller_id = %s
            """, (title, stock, category_id, expiry, image_filename, mrp, description, delivery, product_id, seller_id))
        else:
            # Update without changing the image
            cursor.execute("""
                UPDATE Product
                SET product_title = %s, product_stock = %s, product_category_id = %s,
                    product_expiry = %s, product_mrp = %s, product_description = %s,
                    delivery_available = %s
                WHERE product_id = %s AND seller_id = %s
            """, (title, stock, category_id, expiry, mrp, description, delivery, product_id, seller_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("Product updated successfully!")
        return redirect(url_for('my_products'))

    else:
        # Fetch the product details for pre-filling the form
        seller_id = session.get('user_id')
        cursor.execute("""
            SELECT * FROM Product WHERE product_id = %s AND seller_id = %s
        """, (product_id, seller_id))
        product = cursor.fetchone()

        if not product:
            flash("Unauthorized access or product not found.", "danger")
            return redirect(url_for('my_products'))

        # Fetch the categories to populate the dropdown
        cursor.execute("SELECT * FROM ProductCategory")
        categories = cursor.fetchall()

        cursor.close()
        connection.close()
        
        # Render the edit form with pre-filled product details
        return render_template('edit_product.html', product=product, categories=categories)


@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@role_required('seller')
def delete_product(product_id):
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
       
        delete_query = "DELETE FROM Product WHERE product_id = %s AND seller_id = %s"
        seller_id = session.get('user_id')  
        cursor.execute(delete_query, (product_id, seller_id))
        
        connection.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        connection.rollback()
        flash("An error occurred while deleting the product.", "danger")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('my_products'))

@app.route('/seller/transactions', methods=['GET'])
@login_required
@role_required('seller')
def seller_transactions():
    seller_id = session.get('user_id')
    print("seller id=",seller_id)
    
    if not seller_id:
        flash('Please log in to view your transactions.', 'warning')
        return redirect(url_for('seller_login'))
    
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to fetch transactions
    cursor.execute("""
    SELECT 
        t.transaction_id,
        t.transaction_date,
        t.transaction_status,
        b.buyer_id,
        b.name AS name,
        
        oi.product_id,
        p.product_title,
        oi.quantity,
        oi.total_price,
        t.amount AS transaction_amount
    FROM 
        Transaction t
    JOIN 
        Orders o ON t.order_id = o.order_id
    JOIN 
        OrderItem oi ON o.order_id = oi.order_id
    JOIN 
        Product p ON oi.product_id = p.product_id
    JOIN 
        Buyer b ON o.buyer_id = b.buyer_id
    WHERE 
        t.seller_id = %s
    ORDER BY 
        t.transaction_date DESC
    """, (seller_id,))
    
    transactions = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('seller_transaction.html', transactions=transactions)






@app.route('/buyer_dashboard', methods=['GET', 'POST'])
@login_required
@role_required('buyer')
def buyer_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 9  
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '')  

    
    connection = get_db_connection()
    cursor = connection.cursor()

    
    count_query = """
        SELECT COUNT(*) 
        FROM Product
        WHERE product_title LIKE %s
    """
    cursor.execute(count_query, ('%' + search_query + '%',))  
    total_products = cursor.fetchone()[0]  
    total_pages = ceil(total_products / per_page)

    
    product_query = """
        SELECT product_id, product_title, product_mrp, product_image 
        FROM Product
        WHERE product_title LIKE %s
        LIMIT %s OFFSET %s
    """
    cursor.execute(product_query, ('%' + search_query + '%', per_page, offset))
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('buyer_dashboard.html', products=products, current_page=page, total_pages=total_pages, search_query=search_query)

@app.route('/buyer_dashboard/<int:product_id>')
@login_required
@role_required('buyer')
def product_info(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Updated query to fetch seller details
    product_query = """
        SELECT p.product_id, p.product_title, p.product_mrp, p.product_image, 
               p.product_description, p.product_stock, p.delivery_available, 
               s.name AS seller_name, a.city AS seller_city
        FROM Product p
        JOIN Seller s ON p.seller_id = s.seller_id
        LEFT JOIN Address a ON s.address_id = a.address_id
        WHERE p.product_id = %s
    """
    
    cursor.execute(product_query, (product_id,))
    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if not product:
        flash("Product not found or you don't have permission to view this product.", "danger")
        return redirect(url_for('buyer_dashboard'))  

    return render_template('product_info.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
@role_required('buyer')
def add_to_cart(product_id):
    
    quantity = request.form.get('quantity', type=int)
    buyer_id = session.get('user_id')

    if not buyer_id:
        flash('You need to be logged in to add items to the cart.', 'danger')
        return redirect(url_for('buyer_login'))

    
    if quantity is None or quantity <= 0:
        flash('Please enter a valid quantity.', 'danger')
        return redirect(url_for('product_info', product_id=product_id))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    
    cursor.execute("""
        SELECT product_title, product_stock, product_mrp, delivery_available
        FROM Product
        WHERE product_id = %s
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('product_info', product_id=product_id))

    
    if quantity > product['product_stock']:
        flash(f'Only {product["product_stock"]} units of {product["product_title"]} are available.', 'warning')
        return redirect(url_for('product_info', product_id=product_id))

   
    # if not product['delivery_available']:
    #     flash(f'Delivery is not available for {product["product_title"]}.', 'warning')
    #     return redirect(url_for('product_info', product_id=product_id))

    
    cursor.execute("""
        INSERT INTO Cart (buyer_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + %s
    """, (buyer_id, product_id, quantity, quantity))
    connection.commit()

    flash(f'{quantity} units of {product["product_title"]} have been added to your cart.', 'success')
    cursor.close()
    connection.close()

    return redirect(url_for('buyer_dashboard'))



@app.route('/view_cart')
@login_required
@role_required('buyer')
def view_cart():
    buyer_id = session.get('user_id')
    
    if not buyer_id:
        flash('Please log in to view your cart.', 'warning')
        return redirect(url_for('buyer_login'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to fetch cart items for the logged-in buyer
    cursor.execute("""
        SELECT 
            c.product_id,
            p.product_title, 
            c.quantity, 
            p.product_mrp, 
            p.product_stock,
            (c.quantity * p.product_mrp) AS subtotal
        FROM Cart c
        JOIN Product p ON c.product_id = p.product_id
        WHERE c.buyer_id = %s
    """, (buyer_id,))
    cart_items = cursor.fetchall()
    print(cart_items)

    # Calculate total amount
    total_amount = sum(item['subtotal'] for item in cart_items) if cart_items else 0

    cursor.close()
    connection.close()

    if not cart_items:
        flash('Your cart is empty.', 'info')

    return render_template('view_cart.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
@login_required
@role_required('buyer')
def update_cart_quantity(product_id):
    buyer_id = session.get('user_id')
    actions = request.form.get('action')

    if not buyer_id:
        flash('Please log in to update your cart.', 'warning')
        return redirect(url_for('buyer_login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch current quantity and stock
    cursor.execute("""
        SELECT c.quantity, p.product_stock
        FROM Cart c
        JOIN Product p ON c.product_id = p.product_id
        WHERE c.buyer_id = %s AND c.product_id = %s
    """, (buyer_id, product_id))
    cart_item = cursor.fetchone()

    if not cart_item:
        flash('Item not found in cart.', 'danger')
        return redirect(url_for('view_cart'))

    current_quantity = cart_item['quantity']
    max_stock = cart_item['product_stock']

    # Determine new quantity based on the action
    if actions == 'increment' and current_quantity < max_stock:
        new_quantity = current_quantity + 1
    elif actions == 'decrement' and current_quantity > 1:
        new_quantity = current_quantity - 1
    else:
        new_quantity = current_quantity

    # Update the cart quantity
    cursor.execute("""
        UPDATE Cart
        SET quantity = %s
        WHERE buyer_id = %s AND product_id = %s
    """, (new_quantity, buyer_id, product_id))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Cart updated successfully.', 'success')
    return redirect(url_for('view_cart'))



@app.route('/delete_from_cart/<int:product_id>', methods=['POST'])
@login_required
@role_required('buyer')
def delete_from_cart(product_id):
    buyer_id = session.get('user_id')

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
       
        cursor.execute("""
        DELETE FROM Cart
        WHERE buyer_id = %s AND product_id = %s
    """, (buyer_id, product_id))
        connection.commit()

        flash('Item removed from your cart.', 'success')
    except Exception as e:
        connection.rollback()
        flash("An error occurred while deleting the product.", "danger")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required('buyer')
def checkout():
    payment_method = request.form.get('paymentOption')
    
    buyer_id = session.get('user_id')
    
    if not buyer_id:
        flash('Please log in to view your cart.', 'warning')
        return redirect(url_for('buyer_login'))

    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch the buyer address
    cursor.execute("""
    SELECT * FROM Address 
    WHERE address_id = (SELECT address_id FROM Buyer WHERE buyer_id = %s)
    """, (buyer_id,))
    existing_address = cursor.fetchone()

    if not existing_address:
        flash('Please add a delivery address before placing an order.', 'warning')
        return redirect(url_for('add_address'))

    try:
        # Query to fetch cart items, product stock, and delivery availability
        cursor.execute("""
        SELECT 
            c.product_id,
            p.product_title,
            p.product_stock,
            p.delivery_available,
            (c.quantity * p.product_mrp) AS subtotal,
            c.quantity
        FROM Cart c
        JOIN Product p ON c.product_id = p.product_id
        WHERE c.buyer_id = %s
        """, (buyer_id,))
        cart_items = cursor.fetchall()
    
        if not cart_items:
            flash('Your cart is empty. Add products to the cart before proceeding.', 'warning')
            return redirect(url_for('view_cart'))
    
        # Calculate total amount
        total_amount = sum(item['subtotal'] for item in cart_items) if cart_items else 0
    
        if request.method == 'POST':
            # Step 1: Insert into Orders table
            cursor.execute("""
            INSERT INTO Orders (buyer_id, total_amount, order_status)
            VALUES (%s, %s, 'completed')
            """, (buyer_id, total_amount))
            order_id = cursor.lastrowid  # Get the generated order_id
    
            # Step 2: Insert into OrderItem table and update product stock
            for item in cart_items:
                if item['quantity'] > item['product_stock']:
                    flash(f"Insufficient stock for {item['product_title']}.", 'danger')
                    return redirect(url_for('checkout'))
    
                # Insert item into OrderItem table
                cursor.execute("""
                INSERT INTO OrderItem (order_id, product_id, quantity, total_price)
                VALUES (%s, %s, %s, %s)
                """, (order_id, item['product_id'], item['quantity'], item['subtotal']))
    
                # Update the product stock after placing the order
                cursor.execute("""
                UPDATE Product
                SET product_stock = product_stock - %s
                WHERE product_id = %s
                """, (item['quantity'], item['product_id']))
    
            # Step 3: Insert payment details into Payment table
            payment_status = 'Completed' if payment_method in ['UPI', 'Credit Card', 'Debit Card'] else 'Pending'
            cursor.execute("""
            INSERT INTO Payment (order_id, payment_method, payment_status)
            VALUES (%s, %s, %s)
            """, (order_id, payment_method, payment_status))
            payment_id = cursor.lastrowid  # Get the generated payment_id
    
    
            # Step 5: Empty the Cart
            cursor.execute("""
            DELETE FROM Cart WHERE buyer_id = %s
            """, (buyer_id,))
    
            # Commit the changes to the database
            connection.commit()
    
            flash('Your order has been placed successfully!', 'success')
            
            return redirect(url_for('order_confirmation', order_id=order_id))

    except Exception as e:
    # Rollback the transaction in case of an error
        connection.rollback()
        # Create a pending order to track the failure
        cursor.execute("""
        INSERT INTO Orders (buyer_id, total_amount, order_status)
        VALUES (%s, %s, %s)
        """, (buyer_id, total_amount, 'Pending'))
        connection.commit()
        flash('Error placing order. Please try again.', 'danger')
        return redirect(url_for('view_cart'))

    finally:
        cursor.close()
        connection.close()

    return render_template('checkout.html', cart_items=cart_items, total_amount=total_amount, existing_address=existing_address)

@app.route('/add_address', methods=['GET', 'POST'])
@login_required
@role_required('buyer')
def add_address():
    buyer_id = session.get('user_id')  # Ensure `buyer_id` is retrieved from the session

    if request.method == 'POST':
        street = request.form.get('street')
        city = request.form.get('city')
        region = request.form.get('region')
        pincode = request.form.get('pincode')
        country = request.form.get('country')

        # Validate required fields
        if not all([street, city, pincode, country]):
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('add_address'))

        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert the new address into the Address table
        cursor.execute("""
            INSERT INTO Address (street, city, region, pincode, country)
            VALUES (%s, %s, %s, %s, %s)
        """, (street, city, region, pincode, country))
        address_id = cursor.lastrowid  # Get the newly inserted address ID

        # Link the address with the buyer in the BuyerAddress table
        cursor.execute("""
            INSERT INTO BuyerAddress (buyer_id, address_id)
            VALUES (%s, %s)
        """, (buyer_id, address_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash('Address added successfully!', 'success')
        return redirect(url_for('addresses'))

    return render_template('add_address.html')



@app.route('/addresses', methods=['GET'])
@login_required
@role_required('buyer')
def addresses():
    buyer_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch all addresses associated with the buyer
    cursor.execute("""
        SELECT a.*, 
               (b.address_id = a.address_id) AS is_default  -- Highlight the default address
        FROM Address a
        INNER JOIN BuyerAddress ba ON a.address_id = ba.address_id
        LEFT JOIN Buyer b ON b.buyer_id = ba.buyer_id
        WHERE ba.buyer_id = %s
    """, (buyer_id,))
    addresses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('addresses.html', addresses=addresses)

@app.route('/set_default_address/<int:address_id>', methods=['POST'])
@login_required
@role_required('buyer')
def set_default_address(address_id):
    buyer_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor()

    # Update the default address for the buyer
    cursor.execute("""
        UPDATE Buyer
        SET address_id = %s
        WHERE buyer_id = %s
    """, (address_id, buyer_id))

    connection.commit()
    cursor.close()
    connection.close()

    flash('Default address updated successfully.', 'success')
    return redirect(url_for('addresses'))


@app.route('/edit_address/<int:address_id>', methods=['GET', 'POST'])
@login_required
@role_required('buyer')
def edit_address(address_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch the current address
    cursor.execute("SELECT * FROM Address WHERE address_id = %s", (address_id,))
    address = cursor.fetchone()

    if not address:
        flash('Address not found.', 'danger')
        return redirect(url_for('addresses'))

    if request.method == 'POST':
        # Extract form data
        street = request.form.get('street')
        city = request.form.get('city')
        region = request.form.get('region')
        pincode = request.form.get('pincode')
        country = request.form.get('country')

        # Ensure all required fields are filled
        if not all([street, city, pincode, country]):
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('edit_address', address_id=address_id))

        # Update the address
        cursor.execute("""
            UPDATE Address
            SET street = %s, city = %s, region = %s, pincode = %s, country = %s
            WHERE address_id = %s
        """, (street, city, region, pincode, country, address_id))
        connection.commit()

        flash('Address updated successfully!', 'success')
        return redirect(url_for('addresses'))

    cursor.close()
    connection.close()

    return render_template('edit_address.html', address=address)

@app.route('/order_summary/<int:order_id>', methods=['GET'])
@login_required
@role_required('buyer')
def order_summary(order_id):
    buyer_id = session.get('user_id')
    
    if not buyer_id:
        flash('Please log in to view your order.', 'warning')
        return redirect(url_for('buyer_login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

     # Fetch order details for the given order_id
    cursor.execute("""
    SELECT o.order_id, o.total_amount, o.created_at, o.order_status,
           p.payment_method, p.payment_status
    FROM Orders o
    LEFT JOIN Payment p ON o.order_id = p.order_id
    WHERE o.order_id = %s AND o.buyer_id = %s
    """, (order_id, buyer_id))
    order = cursor.fetchone()

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('view_orders'))  # Redirect to orders list if order not found

    # Fetch the order items
    cursor.execute("""
    SELECT oi.order_item_id, p.product_title, oi.quantity, oi.total_price
    FROM OrderItem oi
    JOIN Product p ON oi.product_id = p.product_id
    WHERE oi.order_id = %s
    """, (order_id,))
    order_items = cursor.fetchall()

    # Fetch the buyer's delivery address
    cursor.execute("""
    SELECT * FROM Address 
    WHERE address_id = (SELECT address_id FROM Buyer WHERE buyer_id = %s)
    """, (buyer_id,))
    address = cursor.fetchone()

    

    cursor.close()
    connection.close()

    return render_template('order_summary.html', order=order, order_items=order_items, address=address)

@app.route('/view_orders')
@login_required
@role_required('buyer')
def view_orders():
    buyer_id = session.get('user_id')

    if not buyer_id:
        flash('Please log in to view your orders.', 'warning')
        return redirect(url_for('buyer_login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT o.order_id, o.total_amount, o.created_at, o.order_status, 
           p.payment_method, p.payment_status
    FROM Orders o
    LEFT JOIN Payment p ON o.order_id = p.order_id
    WHERE o.buyer_id = %s
    ORDER BY o.created_at DESC
    """, (buyer_id,))
    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('view_orders.html', orders=orders)

@app.route('/order_confirmation/<int:order_id>', methods=['GET'])
@login_required
@role_required('buyer')
def order_confirmation(order_id):
    buyer_id = session.get('user_id')
    
    if not buyer_id:
        flash('Please log in to view your order confirmation.', 'warning')
        return redirect(url_for('buyer_login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch order details along with payment details
    cursor.execute("""
    SELECT o.order_id, o.total_amount, o.created_at, o.order_status, 
           p.payment_method, p.payment_status
    FROM Orders o
    LEFT JOIN Payment p ON o.order_id = p.order_id
    WHERE o.order_id = %s AND o.buyer_id = %s
    """, (order_id, buyer_id))
    order = cursor.fetchone()
    

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('view_orders'))

    cursor.close()
    connection.close()

    return render_template('order_confirmation.html', order=order)



@app.route('/logout')
@login_required
def logout():
    session.clear()

    flash("You have been logged out.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 
