import os
import time  # <-- Add this to introduce a delay for MySQL readiness
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'mysql')  # Use 'mysql' instead of 'localhost'
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'flaskdb')

# Initialize MySQL
mysql = MySQL(app)

def wait_for_db():
    """Wait until the database is ready before proceeding."""
    retries = 10  # Number of retries
    for i in range(retries):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1")  # Check if DB is accessible
            cur.close()
            print("Database is ready!")
            return
        except Exception as e:
            print(f"Database connection failed: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
    print("Database connection failed after retries. Exiting.")
    exit(1)

def init_db():
    """Initialize the database."""
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT
        );
        ''')
        mysql.connection.commit()
        cur.close()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    wait_for_db()  # Ensure MySQL is ready before initializing
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
