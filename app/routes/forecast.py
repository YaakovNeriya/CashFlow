from flask import Blueprint, render_template
from datetime import date
import json

from app.db import get_all_transactions, get_all_recurring, get_settings
from app.services.forecast_service import generate_forecast_timeline, calculate_running_balance
from app.services.kpi_service import calculate_kpis, get_chart_data

forecast_bp = Blueprint('forecast', __name__)


@forecast_bp.route('/')
def forecast():
    settings = get_settings()
    start_balance = settings['initial_balance']
    warning_threshold = settings['warning_threshold']
    
    transactions = get_all_transactions()
    recurring_transactions = get_all_recurring()
    
    timeline = generate_forecast_timeline(transactions, recurring_transactions, start_date=date.today(), years_ahead=1)
    running_balance_data = calculate_running_balance(start_balance, timeline, warning_threshold)
    kpis = calculate_kpis(running_balance_data, start_balance, warning_threshold)
    chart_data = get_chart_data(running_balance_data, warning_threshold)
    
    return render_template('forecast.html', 
                           data=running_balance_data,
                           kpis=kpis,
                           chart_data=json.dumps(chart_data),
                           start_balance=start_balance,
                           warning_threshold=warning_threshold)
