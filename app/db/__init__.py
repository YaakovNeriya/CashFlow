# app/db — Data Access Layer
# Re-exports all DB functions for backward compatibility

from app.db.connection import connect, create_tables
from app.db.settings import init_db, get_settings, update_settings
from app.db.transactions import (
    get_all_transactions, add_transaction, 
    delete_transaction, update_transaction
)
from app.db.recurring import (
    get_all_recurring, add_recurring, 
    delete_recurring, update_recurring
)
