import pytest
import cashflow_db

def test_add_and_get_transaction():
    # שלב ההכנה: הוספת רשומה זמנית למסד הנתונים
    test_desc = "TEST_TRANSACTION_CI_CD"
    cashflow_db.add_transaction("2026-05-24", test_desc, 999.0)

    # שלב הפעולה: שליפת כל הרשומות
    transactions = cashflow_db.get_all_transactions()

    # שלב האימות: בדיקה שהרשומה שלנו קיימת
    found = False
    tx_id = None
    for tx in transactions:
        if tx['description'] == test_desc:
            found = True
            tx_id = tx['id']
            break

    # הבדיקה עצמה - אם זה שקר, הטסט ייכשל
    assert found == True

    # שלב הניקיון: מחיקת הרשומה כדי לא ללכלך את מסד הנתונים
    if tx_id:
        cashflow_db.delete_transaction(tx_id) 