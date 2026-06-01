import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────
# GET routes — should return 200
# ─────────────────────────────────────────────

@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.get_settings', return_value={'initial_balance': 1000.0, 'warning_threshold': 500.0})
def test_forecast_returns_200(mock_settings, mock_tx, mock_rec, client):
    response = client.get('/')
    assert response.status_code == 200


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
def test_operations_page_returns_200(mock_tx, mock_rec, client):
    response = client.get('/operations')
    assert response.status_code == 200


@patch('cashflow_db.get_settings', return_value={'initial_balance': 1000.0, 'warning_threshold': 500.0})
def test_settings_page_returns_200(mock_settings, client):
    response = client.get('/settings')
    assert response.status_code == 200


# ─────────────────────────────────────────────
# POST /operations — transactions
# ─────────────────────────────────────────────

@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_transaction', return_value=None)
def test_add_transaction_valid(mock_add, mock_get_tx, mock_get_rec, client):
    response = client.post('/operations', data={
        'form_type': 'transaction',
        'date': '2025-01-15',
        'description': 'Salary',
        'amount': '3000'
    })
    assert response.status_code == 302
    mock_add.assert_called_once_with('2025-01-15', 'Salary', 3000.0)


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_transaction', return_value=None)
def test_add_transaction_invalid_amount(mock_add, mock_get_tx, mock_get_rec, client):
    response = client.post('/operations', data={
        'form_type': 'transaction',
        'date': '2025-01-15',
        'description': 'Test',
        'amount': 'not_a_number'
    })
    assert response.status_code == 302
    mock_add.assert_not_called()


# ─────────────────────────────────────────────
# POST /transactions/delete/<id>
# ─────────────────────────────────────────────

@patch('cashflow_db.delete_transaction', return_value=None)
def test_delete_transaction(mock_delete, client):
    response = client.post('/transactions/delete/1')
    assert response.status_code == 302
    mock_delete.assert_called_once_with(1)


# ─────────────────────────────────────────────
# POST /operations — recurring
# ─────────────────────────────────────────────

@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_recurring', return_value=None)
def test_add_recurring_valid(mock_add, mock_get_tx, mock_get_rec, client):
    response = client.post('/operations', data={
        'form_type': 'recurring',
        'description': 'Rent',
        'amount': '-1500',
        'day_of_month': '5'
    })
    assert response.status_code == 302
    mock_add.assert_called_once_with(5, 'Rent', -1500.0)


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_recurring', return_value=None)
def test_add_recurring_invalid_day(mock_add, mock_get_tx, mock_get_rec, client):
    response = client.post('/operations', data={
        'form_type': 'recurring',
        'description': 'Test',
        'amount': '-100',
        'day_of_month': '32'
    })
    assert response.status_code == 302
    mock_add.assert_not_called()


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_recurring', return_value=None)
def test_add_recurring_day_zero(mock_add, mock_get_tx, mock_get_rec, client):
    response = client.post('/operations', data={
        'form_type': 'recurring',
        'description': 'Test',
        'amount': '-100',
        'day_of_month': '0'
    })
    assert response.status_code == 302
    mock_add.assert_not_called()


# ─────────────────────────────────────────────
# POST /recurring/delete/<id>
# ─────────────────────────────────────────────

@patch('cashflow_db.delete_recurring', return_value=None)
def test_delete_recurring(mock_delete, client):
    response = client.post('/recurring/delete/1')
    assert response.status_code == 302
    mock_delete.assert_called_once_with(1)


# ─────────────────────────────────────────────
# POST /settings
# ─────────────────────────────────────────────

@patch('cashflow_db.get_settings', return_value={'initial_balance': 1000.0, 'warning_threshold': 500.0})
@patch('cashflow_db.update_settings', return_value=None)
def test_update_settings_valid(mock_update, mock_get, client):
    response = client.post('/settings', data={
        'initial_balance': '5000',
        'warning_threshold': '2000'
    })
    assert response.status_code == 302
    mock_update.assert_called_once_with(5000.0, 2000.0)


@patch('cashflow_db.get_settings', return_value={'initial_balance': 1000.0, 'warning_threshold': 500.0})
@patch('cashflow_db.update_settings', return_value=None)
def test_update_settings_invalid(mock_update, mock_get, client):
    response = client.post('/settings', data={'initial_balance': 'abc'})
    assert response.status_code == 302
    mock_update.assert_not_called()