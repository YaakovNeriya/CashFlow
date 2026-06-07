from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.db import get_settings, update_settings

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        try:
            new_balance = float(request.form.get('initial_balance', 0))
            new_threshold = float(request.form.get('warning_threshold', 0))
            update_settings(new_balance, new_threshold)
            flash('ההגדרות עודכנו בהצלחה!', 'success')
        except ValueError:
            flash('ערך לא תקין.', 'error')
        return redirect(url_for('settings.settings'))
    
    current_settings = get_settings()
    return render_template('settings.html', settings=current_settings)
