# Backward-compatibility wrapper — all logic moved to app/services/
# This file re-exports everything so existing imports (e.g. in tests) still work.
from app.services.forecast_service import (
    generate_forecast_timeline,
    calculate_running_balance,
    calculate_monthly_summary
)
from app.services.kpi_service import calculate_kpis, get_chart_data
