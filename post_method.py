from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
import os
from werkzeug.security import check_password_hash, generate_password_hash

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
def index():
    # Check if the user is already logged in
    if 'user_id' in session and 'role' in session:
        if session['role'] == 'buyer':
            return redirect(url_for('buyer_dashboard'))  # Redirect to buyer's dashboard if logged in as buyer
        elif session['role'] == 'seller':
            return redirect(url_for('add_product'))  # Redirect to seller's add product page if logged in as seller
    return render_template('sellerindex.html')  # Show role selection page if not logged in

@app.route('/role_selection', methods=['POST'])
def role_selection():
    role = request.form['role']
    if role == 'buyer':
        return redirect(url_for('buyer_login'))
    elif role == 'seller':
        return redirect(url_for('seller_login'))

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
            session['user_id'] = user['buyer_id']  # Use the actual user ID column name
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
            session['user_id'] = user['seller_id']  # Use the actual user ID column name
            session['role'] = 'seller'
            flash("Login successful!", "success")  # Flash success message
            return redirect(url_for('add_product'))
        else:
            flash("Invalid credentials!", "error")  # Flash error message
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

    # Render the signup form if the request is GET
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
        gst=request.form['GST']

        # Hash the password before saving to database
        hashed_password = generate_password_hash(password)

        # Connect to the database and insert buyer data
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Seller (name, username, email, password, phone1, phone2,gst_number)
                VALUES (%s, %s, %s, %s, %s, %s,%s)
            """, (name, username, email, hashed_password, phone1, phone2,gst))
            connection.commit()
            flash("Signup successful! You can now log in.","success")
            return redirect(url_for('seller_login'))

        except mysql.connector.IntegrityError:
            flash("Username or email already exists. Please try again.","error")
            return redirect(url_for('seller_signup'))

        finally:
            cursor.close()
            connection.close()

    # Render the signup form if the request is GET
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

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Product 
            (product_title, product_stock, product_category_id, product_expiry, product_image, product_mrp, product_description, delivery_available) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, stock, category_id, expiry, image_filename, mrp, description, delivery))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("Product added successfully!")
        return redirect(url_for('add_product'))

    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ProductCategory")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('add_product.html', categories=categories)

@app.route('/logout')
@login_required
def logout():
    session.clear()

    flash("You have been logged out.")
    return redirect(url_for('index'))

@app.route('/buyer_dashboard')
@login_required
@role_required('buyer')
def buyer_dashboard():
    return render_template('buyer_dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
