from flask import Flask, request, render_template, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key'

# Database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rathi@123",
        database="faker"
    )
    return connection

@app.route('/', methods=['GET', 'POST'])
def execute_query():
    if request.method == 'POST':
        query = request.form.get('sql_query')
        if not query:
            flash('Please enter a query.')
            return render_template('execute_query.html')

        try:
            # Connect to the database and execute the query
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            columns = cursor.column_names  # Get column names for table headers

            cursor.close()
            connection.close()

            return render_template('execute_query.html', results=results, columns=columns, querys=query)
        except Exception as e:
            flash(f"Error: {str(e)}")
            return render_template('execute_query.html', querys=query)

    return render_template('execute_query.html')

if __name__ == '__main__':
    app.run(debug=True)
