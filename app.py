from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import cashflow_db
from datetime import date, datetime
from services.analysis_service import generate_forecast_timeline, calculate_running_balance, calculate_monthly_summary, calculate_kpis, get_chart_data
import os
import json

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-fallback-key')
metrics = PrometheusMetrics(app)

# Initialize the db on startup
with app.app_context():
    cashflow_db.init_db()

# ── Screen 2: Forecast Dashboard (Main Screen) ──────────────────────
@app.route('/')
def forecast():
    settings = cashflow_db.get_settings()
    start_balance = settings['initial_balance']
    warning_threshold = settings['warning_threshold']
    
    transactions = cashflow_db.get_all_transactions()
    recurring_transactions = cashflow_db.get_all_recurring()
    
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

# ── Screen 1: Operations (Transactions + Recurring) ─────────────────
@app.route('/operations', methods=['GET', 'POST'])
def operations():
    action = request.args.get('action', '')
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'transaction':
            date_str = request.form.get('date')
            description = request.form.get('description')
            amount_str = request.form.get('amount')
            try:
                if not date_str:
                    raise ValueError("יש להזין תאריך")
                datetime.strptime(date_str, '%Y-%m-%d') # Validate format
                amount_val = float(amount_str)
                cashflow_db.add_transaction(date_str, description, amount_val)
                flash('הפעולה נוספה בהצלחה!', 'success')
            except Exception as e:
                flash(f'שגיאה בהוספת פעולה: {e}', 'error')
                
        elif form_type == 'recurring':
            description = request.form.get('description')
            amount_str = request.form.get('amount')
            day_of_month_str = request.form.get('day_of_month')
            try:
                amount_val = float(amount_str)
                day_val = int(day_of_month_str)
                if not (1 <= day_val <= 31):
                    raise ValueError("יום חייב להיות בין 1 ל-31")
                cashflow_db.add_recurring(day_val, description, amount_val)
                flash('פעולה קבועה חודשית נוספה בהצלחה!', 'success')
            except Exception as e:
                flash(f'שגיאה בהוספת פעולה קבועה: {e}', 'error')
                
        return redirect(url_for('operations'))
        
    transactions = cashflow_db.get_all_transactions()
    recurring = cashflow_db.get_all_recurring()
    return render_template('operations.html', transactions=transactions, recurring=recurring)

@app.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    cashflow_db.delete_transaction(id)
    flash('הפעולה נמחקה!', 'success')
    return redirect(url_for('operations'))

@app.route('/recurring/delete/<int:id>', methods=['POST'])
def delete_recurring(id):
    cashflow_db.delete_recurring(id)
    flash('הפעולה הקבועה נמחקה!', 'success')
    return redirect(url_for('operations'))

# ── Screen 3: Settings ──────────────────────────────────────────────
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        try:
            new_balance = float(request.form.get('initial_balance', 0))
            new_threshold = float(request.form.get('warning_threshold', 0))
            cashflow_db.update_settings(new_balance, new_threshold)
            flash('ההגדרות עודכנו בהצלחה!', 'success')
        except ValueError:
            flash('ערך לא תקין.', 'error')
        return redirect(url_for('settings'))
    
    current_settings = cashflow_db.get_settings()
    return render_template('settings.html', settings=current_settings)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
