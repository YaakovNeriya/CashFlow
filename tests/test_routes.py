import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


# Mock padrão para o cashflow_db — retorna dados vazios por defeito
DEFAULT_MOCKS = {
    'cashflow_db.get_settings': {'initial_balance': 1000.0},
    'cashflow_db.get_all_transactions': [],
    'cashflow_db.get_all_recurring': [],
}


def apply_mocks(mocker, overrides={}):
    mocks = {**DEFAULT_MOCKS, **overrides}
    for target, return_value in mocks.items():
        mocker.patch(target, return_value=return_value)


# ─────────────────────────────────────────────
# GET routes — devem retornar 200
# ─────────────────────────────────────────────

@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.get_settings', return_value={'initial_balance': 1000.0})
def test_dashboard_returns_200(mock_settings, mock_tx, mock_rec, client):
    response = client.get('/')
    assert response.status_code == 200


@patch('cashflow_db.get_all_transactions', return_value=[])
def test_transactions_page_returns_200(mock_tx, client):
    response = client.get('/transactions')
    assert response.status_code == 200


@patch('cashflow_db.get_all_recurring', return_value=[])
def test_recurring_page_returns_200(mock_rec, client):
    response = client.get('/recurring')
    assert response.status_code == 200


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.get_all_transactions', return_value=[])
def test_monthly_page_returns_200(mock_tx, mock_rec, client):
    response = client.get('/monthly')
    assert response.status_code == 200


# ─────────────────────────────────────────────
# POST /transactions
# ─────────────────────────────────────────────

@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_transaction', return_value=None)
def test_add_transaction_valid(mock_add, mock_get, client):
    response = client.post('/transactions', data={
        'date': '2025-01-15',
        'description': 'Salário',
        'amount': '3000'
    })
    assert response.status_code == 302
    mock_add.assert_called_once_with('2025-01-15', 'Salário', 3000.0)


@patch('cashflow_db.get_all_transactions', return_value=[])
@patch('cashflow_db.add_transaction', return_value=None)
def test_add_transaction_invalid_amount(mock_add, mock_get, client):
    response = client.post('/transactions', data={
        'date': '2025-01-15',
        'description': 'Teste',
        'amount': 'nao_e_numero'
    })
    # Deve redirecionar mas sem chamar add_transaction
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
# POST /recurring
# ─────────────────────────────────────────────

@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.add_recurring', return_value=None)
def test_add_recurring_valid(mock_add, mock_get, client):
    response = client.post('/recurring', data={
        'description': 'Aluguel',
        'amount': '-1500',
        'day_of_month': '5'
    })
    assert response.status_code == 302
    mock_add.assert_called_once_with(5, 'Aluguel', -1500.0)


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.add_recurring', return_value=None)
def test_add_recurring_invalid_day(mock_add, mock_get, client):
    response = client.post('/recurring', data={
        'description': 'Teste',
        'amount': '-100',
        'day_of_month': '32'  # inválido
    })
    assert response.status_code == 302
    mock_add.assert_not_called()


@patch('cashflow_db.get_all_recurring', return_value=[])
@patch('cashflow_db.add_recurring', return_value=None)
def test_add_recurring_day_zero(mock_add, mock_get, client):
    response = client.post('/recurring', data={
        'description': 'Teste',
        'amount': '-100',
        'day_of_month': '0'  # inválido
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

@patch('cashflow_db.update_settings', return_value=None)
def test_update_settings_valid(mock_update, client):
    response = client.post('/settings', data={'initial_balance': '5000'})
    assert response.status_code == 302
    mock_update.assert_called_once_with(5000.0)


@patch('cashflow_db.update_settings', return_value=None)
def test_update_settings_invalid(mock_update, client):
    response = client.post('/settings', data={'initial_balance': 'abc'})
    assert response.status_code == 302
    mock_update.assert_not_called()