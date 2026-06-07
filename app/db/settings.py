from app.db.connection import connect, create_tables
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
