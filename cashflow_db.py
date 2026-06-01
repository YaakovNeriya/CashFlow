from cashflow_sql import connect, create_tables
import time

def init_db():
    # Wait for MySQL to be ready
    for i in range(5):
        try:
            with connect() as conn:
                create_tables(conn)
                with conn.cursor() as cursor:
                    # Migrate: add warning_threshold if it doesn't exist
                    cursor.execute("""
                        SELECT COUNT(*) as cnt FROM information_schema.columns
                        WHERE table_schema = DATABASE()
                        AND table_name = 'settings'
                        AND column_name = 'warning_threshold'
                    """)
                    if cursor.fetchone()['cnt'] == 0:
                        cursor.execute("ALTER TABLE settings ADD COLUMN warning_threshold REAL NOT NULL DEFAULT 0.0")

                    cursor.execute("SELECT id FROM settings LIMIT 1")
                    row = cursor.fetchone()
                    if not row:
                        cursor.execute("INSERT INTO settings (initial_balance, warning_threshold) VALUES (0.0, 0.0)")
                conn.commit()
            print("Database connected successfully!")
            return
        except Exception as e:
            print(f"Waiting for database... attempt {i+1}/5")
            time.sleep(3)
    print("ERROR: Could not connect to database after 5 attempts!")


def get_settings():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT initial_balance, warning_threshold FROM settings LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else {'initial_balance': 0.0, 'warning_threshold': 0.0}

def update_settings(initial_balance, warning_threshold):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE settings SET initial_balance = %s, warning_threshold = %s", (initial_balance, warning_threshold))
        conn.commit()

def dict_val(row):
    return dict(row)

# -- TRANSACTIONS --

def get_all_transactions():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, date, description, amount FROM transactions ORDER BY date ASC")
            rows = cursor.fetchall()
            return [dict_val(r) for r in rows]

def add_transaction(date_str, description, amount):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO transactions (date, description, amount) VALUES (%s, %s, %s)", 
                           (date_str, description, amount))
        conn.commit()

def delete_transaction(tx_id):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM transactions WHERE id = %s", (tx_id,))
        conn.commit()

# -- RECURRING TRANSACTIONS --

def get_all_recurring():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, day_of_month, description, amount FROM recurring_transactions ORDER BY day_of_month ASC")
            rows = cursor.fetchall()
            return [dict_val(r) for r in rows]

def add_recurring(day_of_month, description, amount):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO recurring_transactions (day_of_month, description, amount) VALUES (%s, %s, %s)", 
                           (day_of_month, description, amount))
        conn.commit()

def delete_recurring(rec_id):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM recurring_transactions WHERE id = %s", (rec_id,))
        conn.commit()
