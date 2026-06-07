def calculate_kpis(running_balance_data, start_balance, warning_threshold=0.0):
    """Calculate KPI metrics for the forecast dashboard."""
    events = [item for item in running_balance_data if item['type'] == 'event']
    summaries = [item for item in running_balance_data if item['type'] == 'month_summary']
    
    if not events:
        return {
            'current_balance': start_balance,
            'min_balance': start_balance,
            'min_balance_date': None,
            'avg_monthly_credit': 0.0,
            'avg_monthly_debit': 0.0,
            'avg_monthly_net': 0.0,
            'threshold_violations': 0,
            'warning_threshold': warning_threshold,
        }
    
    # Find minimum projected balance
    min_balance = min(e['running_balance'] for e in events)
    min_balance_event = next(e for e in events if e['running_balance'] == min_balance)
    
    # Monthly averages
    num_months = max(len(summaries), 1)
    total_credit = sum(s['credit'] for s in summaries)
    total_debit = sum(s['debit'] for s in summaries)
    
    # Count threshold violations
    violations = sum(1 for e in events if e.get('below_threshold', False))
    
    return {
        'current_balance': start_balance,
        'min_balance': min_balance,
        'min_balance_date': min_balance_event['date'],
        'avg_monthly_credit': total_credit / num_months,
        'avg_monthly_debit': total_debit / num_months,
        'avg_monthly_net': (total_credit + total_debit) / num_months,
        'threshold_violations': violations,
        'warning_threshold': warning_threshold,
    }


def get_chart_data(running_balance_data, warning_threshold=0.0):
    """Prepare data for the Chart.js line chart."""
    events = [item for item in running_balance_data if item['type'] == 'event']
    
    labels = []
    balances = []
    thresholds = []
    
    for e in events:
        labels.append(e['date'].strftime('%d/%m'))
        balances.append(round(e['running_balance'], 2))
        thresholds.append(round(warning_threshold, 2))
    
    return {
        'labels': labels,
        'balances': balances,
        'thresholds': thresholds,
    }
