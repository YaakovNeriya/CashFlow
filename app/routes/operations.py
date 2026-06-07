from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from app.db import (
    get_all_transactions, add_transaction, delete_transaction, update_transaction,
    get_all_recurring, add_recurring, delete_recurring, update_recurring
)

operations_bp = Blueprint('operations', __name__)


@operations_bp.route('/operations', methods=['GET', 'POST'])
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
                    update_transaction(tx_id, date_str, description, amount_val)
                    flash('הפעולה עודכנה בהצלחה!', 'success')
                else:
                    add_transaction(date_str, description, amount_val)
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
                    update_recurring(rec_id, day_val, description, amount_val)
                    flash('פעולה קבועה חודשית עודכנה בהצלחה!', 'success')
                else:
                    add_recurring(day_val, description, amount_val)
                    flash('פעולה קבועה חודשית נוספה בהצלחה!', 'success')
            except Exception as e:
                flash(f'שגיאה בהוספת פעולה קבועה: {e}', 'error')
                
        return redirect(url_for('operations.operations'))
        
    transactions = get_all_transactions()
    recurring = get_all_recurring()
    return render_template('operations.html', transactions=transactions, recurring=recurring)


@operations_bp.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction_route(id):
    delete_transaction(id)
    flash('הפעולה נמחקה!', 'success')
    return redirect(url_for('operations.operations'))


@operations_bp.route('/recurring/delete/<int:id>', methods=['POST'])
def delete_recurring_route(id):
    delete_recurring(id)
    flash('הפעולה הקבועה נמחקה!', 'success')
    return redirect(url_for('operations.operations'))
