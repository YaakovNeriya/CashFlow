from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import cashflow_db
from datetime import date, datetime
from services.analysis_service import generate_forecast_timeline, calculate_running_balance, calculate_monthly_summary, calculate_kpis, get_chart_data
import os
import json
from prometheus_flask_exporter import PrometheusMetrics
from groq import Groq

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-fallback-key')
metrics = PrometheusMetrics(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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
            tx_id = request.form.get('tx_id')
            date_str = request.form.get('date')
            description = request.form.get('description')
            amount_str = request.form.get('amount')
            try:
                if not date_str:
                    raise ValueError("יש להזין תאריך")
                datetime.strptime(date_str, '%Y-%m-%d') # Validate format
                amount_val = float(amount_str)
                if tx_id:
                    cashflow_db.update_transaction(tx_id, date_str, description, amount_val)
                    flash('הפעולה עודכנה בהצלחה!', 'success')
                else:
                    cashflow_db.add_transaction(date_str, description, amount_val)
                    flash('הפעולה נוספה בהצלחה!', 'success')
            except Exception as e:
                flash(f'שגיאה בהוספת פעולה: {e}', 'error')
                
        elif form_type == 'recurring':
            rec_id = request.form.get('rec_id')
            description = request.form.get('description')
            amount_str = request.form.get('amount')
            day_of_month_str = request.form.get('day_of_month')
            try:
                amount_val = float(amount_str)
                day_val = int(day_of_month_str)
                if not (1 <= day_val <= 31):
                    raise ValueError("יום חייב להיות בין 1 ל-31")
                if rec_id:
                    cashflow_db.update_recurring(rec_id, day_val, description, amount_val)
                    flash('פעולה קבועה חודשית עודכנה בהצלחה!', 'success')
                else:
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
    if not groq_client:
        return jsonify({"error": "Groq API key is missing. Please configure GROQ_API_KEY in the server."}), 500

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    day_name_en = today.strftime('%A')
    
    # Map English day to Hebrew for better LLM context
    hebrew_days = {
        'Sunday': 'ראשון', 'Monday': 'שני', 'Tuesday': 'שלישי',
        'Wednesday': 'רביעי', 'Thursday': 'חמישי', 'Friday': 'שישי', 'Saturday': 'שבת'
    }
    day_name_he = hebrew_days.get(day_name_en, '')

    prompt = f"""You are an expert financial transaction extractor for an Israeli app.
Extract all distinct financial transactions from the user's input in Hebrew.
Today's date is: {today_str} (יום {day_name_he}), and today's day of the month is {today.day}.

Rules:
1. Return ONLY a valid JSON array of objects. No markdown, no backticks, just the raw JSON array.
2. Expenses/purchases → negative amount. Income/deposits → positive amount.
3. Provide a short, clean noun-based description in Hebrew. Do NOT include the amount, .
4. For one-time transactions, provide "date" in YYYY-MM-DD format (calculate relative dates based on today).
5. For recurring/monthly transactions (פעולה קבועה / הוראת קבע / כל חודש):
   - Set "is_recurring" to true.
   - Extract or calculate the "day_of_month" (1-31).
   - CRITICAL: If the input uses relative time like "ממחר" (tomorrow) or "עוד יומיים", you MUST calculate the correct day of the month mathematically relative to today ({today.day}).
   - Only if no day or relative timeframe is specified at all, use {today.day}.

Example output:
[
  {{"date": "2023-10-25", "description": "קניית קפה", "amount": -20.0, "is_recurring": false}},
  {{"description": "ביטוח", "amount": -150.0, "is_recurring": true, "day_of_month": 10}}
]

User Input: {text}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024,
        )
        response_text = response.choices[0].message.content.strip()

        # Clean up possible markdown fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        transactions = json.loads(response_text)

        added_count = 0
        for tx in transactions:
            description = tx.get('description', 'פעולה קולית')
            amount = float(tx.get('amount', 0.0))
            is_recurring = tx.get('is_recurring', False)
            
            if is_recurring:
                day_val = tx.get('day_of_month', today.day)
                try:
                    day_val = int(day_val)
                    if not (1 <= day_val <= 31):
                        day_val = today.day
                except:
                    day_val = today.day
                cashflow_db.add_recurring(day_val, description, amount)
            else:
                date_str = tx.get('date', today_str)
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
