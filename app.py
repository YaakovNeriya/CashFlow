from flask import Flask, render_template, request, redirect, url_for, flash
import cashflow_db
from datetime import date
from services.analysis_service import generate_forecast_timeline, calculate_running_balance, calculate_monthly_summary

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Initialize the db on startup
with app.app_context():
    cashflow_db.init_db()

@app.route('/')
def dashboard():
    settings = cashflow_db.get_settings()
    start_balance = settings['initial_balance']
    
    transactions = cashflow_db.get_all_transactions()
    recurring_transactions = cashflow_db.get_all_recurring()
    
    timeline = generate_forecast_timeline(transactions, recurring_transactions, start_date=date.today(), years_ahead=1)
    
    running_balance_data = calculate_running_balance(start_balance, timeline)
    monthly_data = calculate_monthly_summary(timeline)
    
    return render_template('dashboard.html', 
                           data=running_balance_data,
                           monthly_data=monthly_data,
                           current_balance=start_balance,
                           start_balance=start_balance)

@app.route('/transactions', methods=['GET', 'POST'])
def view_transactions():
    if request.method == 'POST':
        date_str = request.form.get('date')
        description = request.form.get('description')
        amount_str = request.form.get('amount')
        
        try:
            amount_val = float(amount_str)
            cashflow_db.add_transaction(date_str, description, amount_val)
            flash('Transaction added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding transaction: {e}', 'error')
            
        return redirect(url_for('view_transactions'))
        
    transactions = cashflow_db.get_all_transactions()
    return render_template('transactions.html', transactions=transactions)

@app.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    cashflow_db.delete_transaction(id)
    flash('Transaction deleted!', 'success')
    return redirect(url_for('view_transactions'))

@app.route('/recurring', methods=['GET', 'POST'])
def view_recurring():
    if request.method == 'POST':
        description = request.form.get('description')
        amount_str = request.form.get('amount')
        day_of_month_str = request.form.get('day_of_month')
        
        try:
            amount_val = float(amount_str)
            day_val = int(day_of_month_str)
            if not (1 <= day_val <= 31):
                raise ValueError("Day must be between 1 and 31")
                
            cashflow_db.add_recurring(day_val, description, amount_val)
            flash('Fixed Monthly Action added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding fixed action: {e}', 'error')
            
        return redirect(url_for('view_recurring'))
        
    recurring = cashflow_db.get_all_recurring()
    return render_template('recurring.html', recurring=recurring)

@app.route('/recurring/delete/<int:id>', methods=['POST'])
def delete_recurring(id):
    cashflow_db.delete_recurring(id)
    flash('Fixed Action deleted!', 'success')
    return redirect(url_for('view_recurring'))

@app.route('/monthly')
def view_monthly():
    transactions = cashflow_db.get_all_transactions()
    recurring_transactions = cashflow_db.get_all_recurring()
    timeline = generate_forecast_timeline(transactions, recurring_transactions, start_date=date.today(), years_ahead=1)
    monthly_data = calculate_monthly_summary(timeline)
    return render_template('monthly.html', monthly_data=monthly_data)

@app.route('/settings', methods=['POST'])
def update_settings():
    new_balance_str = request.form.get('initial_balance')
    if new_balance_str is not None:
        try:
            new_balance = float(new_balance_str)
            cashflow_db.update_settings(new_balance)
            flash('Current bank balance updated!', 'success')
        except ValueError:
            flash('Invalid balance amount.', 'error')
            
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
