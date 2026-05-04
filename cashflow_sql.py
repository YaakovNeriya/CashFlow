import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def connect():
    conn = pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'cashflow'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def create_tables(conn):
    with conn.cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        date VARCHAR(10) NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL
                    );''')
                    
        cursor.execute('''CREATE TABLE IF NOT EXISTS recurring_transactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        day_of_month INT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL
                    );''')
                    
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        initial_balance REAL NOT NULL DEFAULT 0.0
                    );''')
    conn.commit()
