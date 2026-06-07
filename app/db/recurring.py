from app.db.connection import connect

def dict_val(row):
    return dict(row)

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

def update_recurring(rec_id, day_of_month, description, amount):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE recurring_transactions SET day_of_month = %s, description = %s, amount = %s WHERE id = %s", 
                           (day_of_month, description, amount, rec_id))
        conn.commit()
