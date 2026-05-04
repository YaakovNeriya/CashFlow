from cashflow_sql import connect, create_tables

def init_db():
    with connect() as conn:
        create_tables(conn)
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM settings LIMIT 1")
            row = cursor.fetchone()
            if not row:
                cursor.execute("INSERT INTO settings (initial_balance) VALUES (0.0)")
        conn.commit()

def get_settings():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT initial_balance FROM settings LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else {'initial_balance': 0.0}

def update_settings(initial_balance):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE settings SET initial_balance = %s", (initial_balance,))
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
