# Backward-compatibility wrapper — all logic moved to app/db/
# This file re-exports everything so existing imports still work.
from app.db.connection import connect, create_tables
