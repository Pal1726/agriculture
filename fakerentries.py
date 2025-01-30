import random
from faker import Faker
import mysql.connector


fake = Faker()


connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Rathi@123",
    database = "faker",
    ssl_disabled=True
)

cursor = connection.cursor()
num_records=100

#check current record count in a table
def get_record_count(table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

# address
if get_record_count("Address") < num_records:
    address_ids = []
    for _ in range(num_records):
        street = fake.street_address()
        city = fake.city()
        region = fake.state()
        pincode = fake.zipcode()
        country = fake.country()
    
        cursor.execute("""
            INSERT INTO Address (street, city, region, pincode, country) 
            VALUES (%s, %s, %s, %s, %s)
        """, (street, city, region, pincode, country))
        address_ids.append(cursor.lastrowid)
connection.commit()



#seller
if get_record_count("Seller") < num_records:
    seller_ids = []
    for _ in range(num_records):
        name = fake.name()
        username = fake.user_name()
        email = fake.email()
        password = fake.password()
        phone1 = fake.phone_number()[:15]
        phone2 = fake.phone_number()[:15]
        gst_number = fake.random_number(digits=15, fix_len=True)
        address_id = random.choice([id for id in range(1, num_records + 1)])

        cursor.execute("""
            INSERT INTO Seller (name, username, email, password, phone1, phone2, gst_number, address_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, username, email, password, phone1, phone2, gst_number, address_id))
        seller_ids.append(cursor.lastrowid)
connection.commit()

# Create a mapping of categories to their respective IDs
category_mapping = {
    'Fruits': 1,
    'Vegetables': 2,
    'Crops': 3,
    'Seeds': 4,
    'Fertilizer': 5,
    'Pesticides': 6
}

# Assuming product_category_ids list is already populated as before
product_category_ids = []
categories = list(category_mapping.keys())
for category in categories:
    cursor.execute("""
        INSERT INTO ProductCategory (product_category_name) 
        VALUES (%s)
    """, (category,))
    product_category_ids.append(cursor.lastrowid)

connection.commit()

#product
if get_record_count("Product") < num_records:
    fruits = ['Apple', 'Mango', 'Watermelon', 'Banana', 'Grapes']
    vegetables = ['Brinjal', 'Carrot', 'Potato', 'Spinach', 'Tomato']
    crops = ['Wheat', 'Rice', 'Barley', 'Corn', 'Oats']
    seeds = ['Sunflower Seeds', 'Pumpkin Seeds', 'Vegetable Seeds', 'Fruit Seeds']
    fertilizers = ['Organic Fertilizer', 'Chemical Fertilizer', 'Liquid Fertilizer']
    pesticides = ['Herbicide', 'Insecticide', 'Fungicide']

    # Combine all categories into a single list
    all_products = fruits + vegetables + crops + seeds + fertilizers + pesticides

    product_ids = []
    for _ in range(100):
        # Select a random product title from the predefined categories
        product_title = random.choice(all_products)

        # Determine the product category based on the title
        if product_title in fruits:
            product_category_id = category_mapping['Fruits']  # 1
        elif product_title in vegetables:
            product_category_id = category_mapping['Vegetables']  # 2
        elif product_title in crops:
            product_category_id = category_mapping['Crops']  # 3
        elif product_title in seeds:
            product_category_id = category_mapping['Seeds']  # 4
        elif product_title in fertilizers:
            product_category_id = category_mapping['Fertilizer']  # 5
        elif product_title in pesticides:
            product_category_id = category_mapping['Pesticides']  # 6
        else:
            continue  # Skip if the product title doesn't match any category

        product_stock = random.randint(1, 100)

        product_expiry = fake.date_between(start_date='today', end_date='+1y')
        product_image = fake.image_url()
        product_mrp = round(random.uniform(1, 100), 2)
        product_description = fake.text(max_nb_chars=200)
        delivery_available = random.choice([True, False])
        seller_id = random.choice(seller_ids)  

        cursor.execute("""
            INSERT INTO Product (product_title, product_stock, product_category_id, product_expiry, 
                             product_image, product_mrp, product_description, delivery_available, seller_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (product_title, product_stock, product_category_id, product_expiry,
              product_image, product_mrp, product_description, delivery_available, seller_id))
        product_ids.append(cursor.lastrowid)

connection.commit()


#buyer
if get_record_count("Buyer") < num_records:
    buyer_ids = []
    for _ in range(100):
        name = fake.name()
        username = fake.user_name()
        email = fake.email()
        password = fake.password()
        max_phone_length=15
        phone1 = fake.phone_number()[:max_phone_length]
        max_phone_length=15
        phone2 = fake.phone_number()[:max_phone_length]
        address_id = random.choice(address_ids)  
    
        cursor.execute("""
            INSERT INTO Buyer (name, username, email, password, phone1, phone2, address_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, username, email, password, phone1, phone2, address_id))
        buyer_ids.append(cursor.lastrowid)

connection.commit()

# BuyerAddress
if get_record_count("BuyerAddress") < num_records:
    for buyer_id in buyer_ids:
        address_id = random.choice(address_ids)
        cursor.execute("""
            INSERT INTO BuyerAddress (buyer_id, address_id) 
            VALUES (%s, %s)
        """, (buyer_id, address_id))
connection.commit()

#cart
if get_record_count("Cart") < num_records:
    for _ in range(100):
        buyer_id = random.choice(buyer_ids)  
        product_id = random.choice(product_ids) 
        quantity = random.randint(1, 50)
    
        cursor.execute("""
            INSERT INTO Cart (buyer_id, product_id, quantity) 
            VALUES (%s, %s, %s)
        """, (buyer_id, product_id, quantity))

connection.commit()



#orders
if get_record_count("Orders") < num_records:
    order_ids = []
    for _ in range(100):
        buyer_id = random.choice(buyer_ids)  
        
        
        
    
        cursor.execute("""
            INSERT INTO Orders (buyer_id) 
            VALUES (%s)
        """, (buyer_id,))
        order_ids.append(cursor.lastrowid)

connection.commit()

#orderItem
if get_record_count("OrderItem") < num_records:
    for _ in range(100):
        order_id = random.choice(order_ids)  # Randomly select an order
        product_id = random.choice(product_ids)  # Randomly select a product
        quantity = random.randint(1, 50)
        
    
        cursor.execute("""
            INSERT INTO OrderItem (order_id, product_id, quantity) 
            VALUES (%s, %s, %s)
        """, (order_id, product_id, quantity))

connection.commit()

# Transactions
if get_record_count("Transaction") < num_records:
    for _ in range(100):
        order_item_id = random.choice(order_ids) 
        buyer_id = random.choice(buyer_ids)  
        seller_id = random.choice(seller_ids)  
        
        transaction_date = fake.date_time_this_year()
        transaction_status = random.choice(['Completed', 'Pending', 'Failed'])
    
        cursor.execute("""
            INSERT INTO Transaction (order_item_id, buyer_id, seller_id, transaction_date, transaction_status) 
            VALUES (%s, %s, %s, %s, %s)
        """, (order_item_id, buyer_id, seller_id, transaction_date, transaction_status))

connection.commit()

#  Payments
if get_record_count("Payment") < num_records:
    for _ in range(100):
        order_id = random.choice(order_ids)  # Randomly select an order
        payment_method = random.choice(['Credit Card', 'Debit Card', 'Net Banking', 'UPI'])
        payment_status = random.choice(['Pending', 'Completed', 'Failed'])
    
        cursor.execute("""
            INSERT INTO Payment (order_id, payment_method, payment_status) 
            VALUES (%s, %s, %s)
        """, (order_id, payment_method, payment_status))

connection.commit()


cursor.close()
connection.close()
