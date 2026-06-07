from app.db.connection import connect

def dict_val(row):
    return dict(row)

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

def update_transaction(tx_id, date_str, description, amount):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE transactions SET date = %s, description = %s, amount = %s WHERE id = %s", 
                           (date_str, description, amount, tx_id))
        conn.commit()
