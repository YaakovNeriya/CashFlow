import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'cashflow.db')

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL
                );''')
                
    conn.execute('''CREATE TABLE IF NOT EXISTS recurring_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day_of_month INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL
                );''')
                
    conn.execute('''CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    initial_balance REAL NOT NULL DEFAULT 0.0
                );''')
    conn.commit()
