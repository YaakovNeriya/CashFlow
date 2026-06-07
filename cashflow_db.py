# Backward-compatibility wrapper — all logic moved to app/db/
# This file re-exports everything so existing imports (e.g. in tests) still work.
from app.db.settings import init_db, get_settings, update_settings
from app.db.transactions import (
    get_all_transactions, add_transaction,
    delete_transaction, update_transaction
)
from app.db.recurring import (
    get_all_recurring, add_recurring,
    delete_recurring, update_recurring
)
