import pytest
from datetime import date
from services.analysis_service import (
    calculate_running_balance,
    calculate_monthly_summary,
    generate_forecast_timeline
)


# ─────────────────────────────────────────────
# calculate_running_balance
# ─────────────────────────────────────────────

def test_running_balance_empty():
    result = calculate_running_balance(1000.0, [])
    assert result == []


def test_running_balance_single_positive():
    events = [{'date': date(2025, 1, 1), 'amount': 500.0, 'description': 'Salário'}]
    result = calculate_running_balance(1000.0, events)
    assert result[0]['running_balance'] == 1500.0


def test_running_balance_single_negative():
    events = [{'date': date(2025, 1, 1), 'amount': -200.0, 'description': 'Aluguel'}]
    result = calculate_running_balance(1000.0, events)
    assert result[0]['running_balance'] == 800.0


def test_running_balance_accumulates():
    events = [
        {'date': date(2025, 1, 1), 'amount': 500.0, 'description': 'Salário'},
        {'date': date(2025, 1, 5), 'amount': -100.0, 'description': 'Mercado'},
        {'date': date(2025, 1, 10), 'amount': -50.0, 'description': 'Transporte'},
    ]
    result = calculate_running_balance(1000.0, events)
    assert result[0]['running_balance'] == 1500.0
    assert result[1]['running_balance'] == 1400.0
    assert result[2]['running_balance'] == 1350.0


def test_running_balance_zero_start():
    events = [{'date': date(2025, 1, 1), 'amount': 300.0, 'description': 'Entrada'}]
    result = calculate_running_balance(0.0, events)
    assert result[0]['running_balance'] == 300.0


def test_running_balance_preserves_original_fields():
    events = [{'date': date(2025, 1, 1), 'amount': 100.0, 'description': 'Teste', 'id': 1}]
    result = calculate_running_balance(0.0, events)
    assert result[0]['description'] == 'Teste'
    assert result[0]['id'] == 1


def test_running_balance_does_not_mutate_original():
    events = [{'date': date(2025, 1, 1), 'amount': 100.0, 'description': 'Teste'}]
    calculate_running_balance(0.0, events)
    assert 'running_balance' not in events[0]


# ─────────────────────────────────────────────
# calculate_monthly_summary
# ─────────────────────────────────────────────

def test_monthly_summary_empty():
    result = calculate_monthly_summary([])
    assert result == []


def test_monthly_summary_single_credit():
    events = [{'date': date(2025, 1, 15), 'amount': 3000.0, 'description': 'Salário'}]
    result = calculate_monthly_summary(events)
    assert len(result) == 1
    assert result[0]['month'] == '2025-01'
    assert result[0]['credit'] == 3000.0
    assert result[0]['debit'] == 0.0
    assert result[0]['net_difference'] == 3000.0


def test_monthly_summary_single_debit():
    events = [{'date': date(2025, 1, 5), 'amount': -500.0, 'description': 'Aluguel'}]
    result = calculate_monthly_summary(events)
    assert result[0]['debit'] == -500.0
    assert result[0]['credit'] == 0.0
    assert result[0]['net_difference'] == -500.0


def test_monthly_summary_net_difference():
    events = [
        {'date': date(2025, 1, 1), 'amount': 3000.0, 'description': 'Salário'},
        {'date': date(2025, 1, 10), 'amount': -1000.0, 'description': 'Aluguel'},
        {'date': date(2025, 1, 20), 'amount': -200.0, 'description': 'Mercado'},
    ]
    result = calculate_monthly_summary(events)
    assert result[0]['net_difference'] == pytest.approx(1800.0)


def test_monthly_summary_multiple_months():
    events = [
        {'date': date(2025, 1, 1), 'amount': 3000.0, 'description': 'Salário Jan'},
        {'date': date(2025, 2, 1), 'amount': 3000.0, 'description': 'Salário Fev'},
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
        {'id': 1, 'date': '2024-12-01', 'description': 'Passado', 'amount': 100.0}
    ]
    result = generate_forecast_timeline(transactions, [], start_date=date(2025, 1, 1))
    descriptions = [e['description'] for e in result]
    assert 'Passado' in descriptions


def test_forecast_recurring_generates_future_events():
    recurring = [
        {'id': 1, 'day_of_month': 5, 'description': 'Aluguel', 'amount': -1500.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1))
    assert len(result) > 0
    assert any('Aluguel' in e['description'] for e in result)


def test_forecast_recurring_has_rec_prefix():
    recurring = [
        {'id': 1, 'day_of_month': 5, 'description': 'Aluguel', 'amount': -1500.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1))
    rec_events = [e for e in result if e['is_recurring']]
    assert all(str(e['id']).startswith('rec_') for e in rec_events)


def test_forecast_recurring_has_hebrew_suffix():
    recurring = [
        {'id': 1, 'day_of_month': 5, 'description': 'Aluguel', 'amount': -1500.0}
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
    # Dia 31 em fevereiro deve cair no último dia do mês
    recurring = [
        {'id': 1, 'day_of_month': 31, 'description': 'Fim do mês', 'amount': -100.0}
    ]
    result = generate_forecast_timeline([], recurring, start_date=date(2025, 2, 1))
    feb_events = [e for e in result if e['date'].month == 2 and e['date'].year == 2025]
    assert len(feb_events) > 0
    assert feb_events[0]['date'].day == 28  # 2025 não é bissexto


def test_forecast_respects_years_ahead():
    result_1yr = generate_forecast_timeline([], [], start_date=date(2025, 1, 1), years_ahead=1)
    result_2yr = generate_forecast_timeline([], [], start_date=date(2025, 1, 1), years_ahead=2)
    # Com mais anos e sem recorrentes, ambos são vazios — mas podemos testar com recorrentes
    recurring = [{'id': 1, 'day_of_month': 1, 'description': 'Teste', 'amount': 100.0}]
    result_1yr = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1), years_ahead=1)
    result_2yr = generate_forecast_timeline([], recurring, start_date=date(2025, 1, 1), years_ahead=2)
    assert len(result_2yr) > len(result_1yr)