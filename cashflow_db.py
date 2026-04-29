from cashflow_sql import connect, create_tables

def init_db():
    with connect() as conn:
        create_tables(conn)
        row = conn.execute("SELECT id FROM settings LIMIT 1").fetchone()
        if not row:
            conn.execute("INSERT INTO settings (initial_balance) VALUES (0.0)")
            conn.commit()

def get_settings():
    with connect() as conn:
        row = conn.execute("SELECT initial_balance FROM settings LIMIT 1").fetchone()
        return dict(row) if row else {'initial_balance': 0.0}

def update_settings(initial_balance):
    with connect() as conn:
        conn.execute("UPDATE settings SET initial_balance = ?", (initial_balance,))
        conn.commit()

def dict_val(row):
    return dict(row)

# -- TRANSACTIONS --

def get_all_transactions():
    with connect() as conn:
        rows = conn.execute("SELECT id, date, description, amount FROM transactions ORDER BY date ASC").fetchall()
        return [dict_val(r) for r in rows]

def add_transaction(date_str, description, amount):
    with connect() as conn:
        conn.execute("INSERT INTO transactions (date, description, amount) VALUES (?, ?, ?)", 
                     (date_str, description, amount))
        conn.commit()

def delete_transaction(tx_id):
    with connect() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()

# -- RECURRING TRANSACTIONS --

def get_all_recurring():
    with connect() as conn:
        rows = conn.execute("SELECT id, day_of_month, description, amount FROM recurring_transactions ORDER BY day_of_month ASC").fetchall()
        return [dict_val(r) for r in rows]

def add_recurring(day_of_month, description, amount):
    with connect() as conn:
        conn.execute("INSERT INTO recurring_transactions (day_of_month, description, amount) VALUES (?, ?, ?)", 
                     (day_of_month, description, amount))
        conn.commit()

def delete_recurring(rec_id):
    with connect() as conn:
        conn.execute("DELETE FROM recurring_transactions WHERE id = ?", (rec_id,))
        conn.commit()
