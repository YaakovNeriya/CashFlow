from collections import defaultdict
from datetime import datetime, date
import calendar

def generate_forecast_timeline(transactions, recurring_transactions, start_date=None, years_ahead=1):
    if start_date is None:
        start_date = date.today()
        
    try:
        end_date = start_date.replace(year=start_date.year + years_ahead)
    except ValueError:
        end_date = start_date.replace(year=start_date.year + years_ahead, day=28)
    
    all_events = []
    
    # 1. Ad-hoc transactions (parsing from dictionaries instead of Objects)
    for t in transactions:
        t_date = datetime.strptime(t['date'], '%Y-%m-%d').date()
        all_events.append({
            'is_recurring': False,
            'id': t['id'],
            'date': t_date,
            'description': t['description'],
            'amount': t['amount']
        })
        
    # 2. Future recurring instances (from dictionaries)
    current_month = start_date.replace(day=1)
    
    while current_month <= end_date:
        _, num_days_in_month = calendar.monthrange(current_month.year, current_month.month)
        
        for rt in recurring_transactions:
            target_day = min(rt['day_of_month'], num_days_in_month)
            target_date = date(current_month.year, current_month.month, target_day)
            
            if start_date <= target_date <= end_date:
                all_events.append({
                    'is_recurring': True,
                    'id': f"rec_{rt['id']}_{target_date.strftime('%Y%m%d')}",
                    'date': target_date,
                    'description': f"{rt['description']} (קבוע)",
                    'amount': rt['amount']
                })
                
        # Move to next month safely
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)
            
    return sorted(all_events, key=lambda x: x['date'])

def calculate_running_balance(start_balance, timeline_events):
    current_balance = start_balance
    result = []
    for t in timeline_events:
        current_balance += t['amount']
        t_copy = t.copy()
        t_copy['running_balance'] = current_balance
        result.append(t_copy)
    return result

def calculate_monthly_summary(timeline_events):
    summary = defaultdict(lambda: {'credit': 0.0, 'debit': 0.0})
    for t in timeline_events:
        month_key = t['date'].strftime('%Y-%m')
        if t['amount'] > 0:
            summary[month_key]['credit'] += t['amount']
        else:
            summary[month_key]['debit'] += t['amount']
            
    result = []
    for month in sorted(summary.keys()):
        credit = summary[month]['credit']
        debit = summary[month]['debit']
        net = credit + debit
        result.append({
            'month': month,
            'credit': credit,
            'debit': debit,
            'net_difference': net
        })
    return result
