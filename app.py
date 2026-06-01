from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import cashflow_db
from datetime import date, datetime
from services.analysis_service import generate_forecast_timeline, calculate_running_balance, calculate_monthly_summary, calculate_kpis, get_chart_data
import os
import json

from prometheus_flask_exporter import PrometheusMetrics
import google.generativeai as genai

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-fallback-key')
metrics = PrometheusMetrics(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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

@app.route('/api/voice_transaction', methods=['POST'])
def voice_transaction():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key is missing. Please configure it in the server."}), 500
        
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    today_str = date.today().strftime('%Y-%m-%d')
    prompt = f"""
    You are a financial transaction extractor.
    Extract all distinct financial transactions from the user's input in Hebrew.
    Today's date is: {today_str}
    
    Rules:
    1. Return ONLY a valid JSON array of objects. Do not include markdown formatting like ```json or backticks. Just the raw array.
    2. If an amount is an expense or purchase (like buying coffee, groceries, paying bills), make it a negative number. 
    3. If an amount is an income or deposit (like salary, getting paid), make it a positive number.
    4. Provide a short description in Hebrew based on the text.
    5. Ensure the date is in YYYY-MM-DD format. If no date is specified, use today's date ({today_str}).
    
    Format example:
    [
      {{"date": "2023-10-25", "description": "קפה", "amount": -20.0}},
      {{"date": "2023-10-25", "description": "משכורת", "amount": 5000.0}}
    ]
    
    User Input: {text}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up possible markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        transactions = json.loads(response_text)
        
        added_count = 0
        for tx in transactions:
            date_str = tx.get('date', today_str)
            description = tx.get('description', 'פעולה קולית')
            amount = float(tx.get('amount', 0.0))
            cashflow_db.add_transaction(date_str, description, amount)
            added_count += 1
            
        return jsonify({"success": True, "added": added_count, "transactions": transactions})
        
    except Exception as e:
        print(f"Error parsing voice transaction: {e}")
        return jsonify({"error": str(e)}), 500

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
