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


def calculate_running_balance(start_balance, timeline_events, warning_threshold=0.0):
    """Calculate running balance and add month markers, warnings, and monthly summaries."""
    current_balance = start_balance
    result = []
    current_month = None
    month_credit = 0.0
    month_debit = 0.0
    month_event_count = 0
    
    for i, t in enumerate(timeline_events):
        event_month = t['date'].strftime('%Y-%m')
        
        # Detect month change — insert monthly summary for previous month
        if current_month is not None and event_month != current_month:
            month_net = month_credit + month_debit
            result.append({
                'type': 'month_summary',
                'month': current_month,
                'credit': month_credit,
                'debit': month_debit,
                'net': month_net,
                'running_balance': current_balance,
                'balance_change': month_net,
            })
            month_credit = 0.0
            month_debit = 0.0
            month_event_count = 0
        
        # Track if this is the first event in a new month
        is_month_start = (event_month != current_month)
        current_month = event_month
        
        current_balance += t['amount']
        month_event_count += 1
        
        if t['amount'] > 0:
            month_credit += t['amount']
        else:
            month_debit += t['amount']
        
        t_copy = t.copy()
        t_copy['type'] = 'event'
        t_copy['running_balance'] = current_balance
        t_copy['is_month_start'] = is_month_start
        t_copy['month_event_count'] = month_event_count
        t_copy['below_threshold'] = (current_balance < warning_threshold) if warning_threshold > 0 else False
        result.append(t_copy)
    
    # Final month summary
    if current_month is not None:
        month_net = month_credit + month_debit
        result.append({
            'type': 'month_summary',
            'month': current_month,
            'credit': month_credit,
            'debit': month_debit,
            'net': month_net,
            'running_balance': current_balance,
            'balance_change': month_net,
        })
    
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
