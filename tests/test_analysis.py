import pytest
from datetime import date
from app.services.forecast_service import (
    calculate_running_balance,
    calculate_monthly_summary,
    generate_forecast_timeline
)
from app.services.kpi_service import calculate_kpis, get_chart_data


# ─────────────────────────────────────────────
# calculate_running_balance
# ─────────────────────────────────────────────

def test_running_balance_empty():
    result = calculate_running_balance(1000.0, [])
    assert result == []


def test_running_balance_single_positive():
    events = [{'date': date(2025, 1, 1), 'amount': 500.0, 'description': 'Salary'}]
    result = calculate_running_balance(1000.0, events)
    event_items = [r for r in result if r['type'] == 'event']
    assert event_items[0]['running_balance'] == 1500.0


def test_running_balance_single_negative():
    events = [{'date': date(2025, 1, 1), 'amount': -200.0, 'description': 'Rent'}]
    result = calculate_running_balance(1000.0, events)
    event_items = [r for r in result if r['type'] == 'event']
    assert event_items[0]['running_balance'] == 800.0


def test_running_balance_accumulates():
    events = [
        {'date': date(2025, 1, 1), 'amount': 500.0, 'description': 'Salary'},
        {'date': date(2025, 1, 5), 'amount': -100.0, 'description': 'Groceries'},
        {'date': date(2025, 1, 10), 'amount': -50.0, 'description': 'Transport'},
    ]
    result = calculate_running_balance(1000.0, events)
    event_items = [r for r in result if r['type'] == 'event']
    assert event_items[0]['running_balance'] == 1500.0
    assert event_items[1]['running_balance'] == 1400.0
    assert event_items[2]['running_balance'] == 1350.0


def test_running_balance_zero_start():
    events = [{'date': date(2025, 1, 1), 'amount': 300.0, 'description': 'Income'}]
    result = calculate_running_balance(0.0, events)
    event_items = [r for r in result if r['type'] == 'event']
    assert event_items[0]['running_balance'] == 300.0


def test_running_balance_preserves_original_fields():
    events = [{'date': date(2025, 1, 1), 'amount': 100.0, 'description': 'Test', 'id': 1}]
    result = calculate_running_balance(0.0, events)
    event_items = [r for r in result if r['type'] == 'event']
    assert event_items[0]['description'] == 'Test'
    assert event_items[0]['id'] == 1


def test_running_balance_does_not_mutate_original():
    events = [{'date': date(2025, 1, 1), 'amount': 100.0, 'description': 'Test'}]
    calculate_running_balance(0.0, events)
    assert 'running_balance' not in events[0]


def test_running_balance_month_start_flag():
    events = [
        {'date': date(2025, 1, 15), 'amount': 100.0, 'description': 'A'},
        {'date': date(2025, 1, 20), 'amount': 100.0, 'description': 'B'},
        {'date': date(2025, 2, 1), 'amount': 100.0, 'description': 'C'},
    ]
    result = calculate_running_balance(0.0, events)
    event_items = [r for r in result if r['type'] == 'event']
    assert event_items[0]['is_month_start'] is True
    assert event_items[1]['is_month_start'] is False
    assert event_items[2]['is_month_start'] is True


def test_running_balance_month_summaries():
    events = [
        {'date': date(2025, 1, 1), 'amount': 500.0, 'description': 'Income'},
        {'date': date(2025, 1, 10), 'amount': -200.0, 'description': 'Expense'},
        {'date': date(2025, 2, 1), 'amount': 300.0, 'description': 'Income2'},
    ]
    result = calculate_running_balance(0.0, events)
    summaries = [r for r in result if r['type'] == 'month_summary']
    assert len(summaries) == 2  # Jan + Feb
    jan_summary = summaries[0]
    assert jan_summary['month'] == '2025-01'
    assert jan_summary['credit'] == 500.0
    assert jan_summary['debit'] == -200.0
    assert jan_summary['net'] == 300.0


def test_running_balance_warning_threshold():
    events = [
        {'date': date(2025, 1, 1), 'amount': -800.0, 'description': 'Big expense'},
    ]
    result = calculate_running_balance(1000.0, events, warning_threshold=500.0)
    event_items = [r for r in result if r['type'] == 'event']
    # balance = 1000 - 800 = 200, which is below 500
    assert event_items[0]['below_threshold'] is True


def test_running_balance_no_warning_when_above_threshold():
    events = [
        {'date': date(2025, 1, 1), 'amount': -100.0, 'description': 'Small expense'},
    ]
    result = calculate_running_balance(1000.0, events, warning_threshold=500.0)
    event_items = [r for r in result if r['type'] == 'event']
    # balance = 1000 - 100 = 900, above 500
    assert event_items[0]['below_threshold'] is False


# ─────────────────────────────────────────────
# calculate_monthly_summary
# ─────────────────────────────────────────────

def test_monthly_summary_empty():
    result = calculate_monthly_summary([])
    assert result == []


def test_monthly_summary_single_credit():
    events = [{'date': date(2025, 1, 15), 'amount': 3000.0, 'description': 'Salary'}]
    result = calculate_monthly_summary(events)
    assert len(result) == 1
    assert result[0]['month'] == '2025-01'
    assert result[0]['credit'] == 3000.0
    assert result[0]['debit'] == 0.0
    assert result[0]['net_difference'] == 3000.0


def test_monthly_summary_single_debit():
    events = [{'date': date(2025, 1, 5), 'amount': -500.0, 'description': 'Rent'}]
    result = calculate_monthly_summary(events)
    assert result[0]['debit'] == -500.0
    assert result[0]['credit'] == 0.0
    assert result[0]['net_difference'] == -500.0


def test_monthly_summary_net_difference():
    events = [
        {'date': date(2025, 1, 1), 'amount': 3000.0, 'description': 'Salary'},
        {'date': date(2025, 1, 10), 'amount': -1000.0, 'description': 'Rent'},
        {'date': date(2025, 1, 20), 'amount': -200.0, 'description': 'Groceries'},
    ]
    result = calculate_monthly_summary(events)
    assert result[0]['net_difference'] == pytest.approx(1800.0)


def test_monthly_summary_multiple_months():
    events = [
        {'date': date(2025, 1, 1), 'amount': 3000.0, 'description': 'Jan Salary'},
        {'date': date(2025, 2, 1), 'amount': 3000.0, 'description': 'Feb Salary'},
    ]
    result = calculate_monthly_summary(events)
    assert len(result) == 2
    assert result[0]['month'] == '2025-01'
    assert result[1]['month'] == '2025-02'


def test_monthly_summary_sorted_by_month():
    events = [
        {'date': date(2025, 3, 1), 'amount': 100.0, 'description': 'C'},
        {'date': date(2025, 1, 1), 'amount': 100.0, 'description': 'A'},
        {'date': date(2025, 2, 1), 'amount': 100.0, 'description': 'B'},
    ]
    result = calculate_monthly_summary(events)
    months = [r['month'] for r in result]
    assert months == ['2025-01', '2025-02', '2025-03']


# ─────────────────────────────────────────────
# generate_forecast_timeline
# ─────────────────────────────────────────────

def test_forecast_empty_inputs():
    result = generate_forecast_timeline([], [], start_date=date(2025, 1, 1))
    assert isinstance(result, list)


def test_forecast_includes_past_transactions():
    transactions = [
        {'id': 1, 'date': '2024-12-01', 'description': 'Past', 'amount': 100.0}
    ]
    result = generate_forecast_timeline(transactions, [], start_date=date(2025, 1, 1))
    descriptions = [e['description'] for e in result]
    assert 'Past' in descriptions


def test_forecast_recurring_generates_future_events():
    recurring = [
        {'id': 1, 'day_of_month': 5, 'description': 'Rent', 'amount': -1500.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1))
    assert len(result) > 0
    assert any('Rent' in e['description'] for e in result)


def test_forecast_recurring_has_rec_prefix():
    recurring = [
        {'id': 1, 'day_of_month': 5, 'description': 'Rent', 'amount': -1500.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1))
    rec_events = [e for e in result if e['is_recurring']]
    assert all(str(e['id']).startswith('rec_') for e in rec_events)


def test_forecast_recurring_has_hebrew_suffix():
    recurring = [
        {'id': 1, 'day_of_month': 5, 'description': 'Rent', 'amount': -1500.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1))
    rec_events = [e for e in result if e['is_recurring']]
    assert all('קבוע' in e['description'] for e in rec_events)


def test_forecast_sorted_by_date():
    transactions = [
        {'id': 1, 'date': '2025-03-01', 'description': 'C', 'amount': 100.0},
        {'id': 2, 'date': '2025-01-01', 'description': 'A', 'amount': 100.0},
        {'id': 3, 'date': '2025-02-01', 'description': 'B', 'amount': 100.0},
    ]
    result = generate_forecast_timeline(transactions, [], start_date=date(2024, 1, 1))
    dates = [e['date'] for e in result if not e['is_recurring']]
    assert dates == sorted(dates)


def test_forecast_recurring_clamps_day_in_short_month():
    recurring = [
        {'id': 1, 'day_of_month': 31, 'description': 'End of month', 'amount': -100.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 2, 1))
    feb_events = [e for e in result if e['date'].month == 2 and e['date'].year == 2025]
    assert len(feb_events) > 0
    assert feb_events[0]['date'].day == 28


def test_forecast_respects_years_ahead():
    recurring = [{'id': 1, 'day_of_month': 1, 'description': 'Test', 'amount': 100.0}]
    result_1yr = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1), years_ahead=1)
    result_2yr = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1), years_ahead=2)
    assert len(result_2yr) > len(result_1yr)


# ─────────────────────────────────────────────
# calculate_kpis
# ─────────────────────────────────────────────

def test_kpis_empty_data():
    result = calculate_kpis([], 1000.0, 500.0)
    assert result['current_balance'] == 1000.0
    assert result['min_balance'] == 1000.0
    assert result['threshold_violations'] == 0


def test_kpis_with_violations():
    events = [
        {'date': date(2025, 1, 1), 'amount': -800.0, 'description': 'Big expense'},
    ]
    data = calculate_running_balance(1000.0, events, warning_threshold=500.0)
    kpis = calculate_kpis(data, 1000.0, 500.0)
    assert kpis['threshold_violations'] == 1
    assert kpis['min_balance'] == 200.0


# ─────────────────────────────────────────────
# get_chart_data
# ─────────────────────────────────────────────

def test_chart_data_empty():
    result = get_chart_data([], 500.0)
    assert result['labels'] == []
    assert result['balances'] == []


def test_chart_data_has_correct_length():
    events = [
        {'date': date(2025, 1, 1), 'amount': 500.0, 'description': 'A'},
        {'date': date(2025, 1, 5), 'amount': -100.0, 'description': 'B'},
    ]
    data = calculate_running_balance(1000.0, events)
    result = get_chart_data(data, 500.0)
    assert len(result['labels']) == 2
    assert len(result['balances']) == 2
    assert len(result['thresholds']) == 2