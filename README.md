# CashFlow 💰

CashFlow is a full-stack personal finance web application built with Python, Flask, and SQLite. It helps you manage your money by tracking daily transactions, handling recurring monthly expenses, and providing intelligent cash flow forecasting so you can easily see your future financial state.

## Features

- **Transaction Management**: Add, view, and delete ad-hoc daily transactions.
- **Recurring Expenses**: Manage fixed monthly actions (e.g., salary, rent, subscriptions) by specifying the day of the month and amount.
- **Cash Flow Forecasting**: Automatically projects your running balance into the future by combining your current balance, ad-hoc transactions, and upcoming recurring actions.
- **Monthly Summaries**: View aggregated data to understand your net cash flow on a month-by-month basis.
- **Modern UI**: A clean, responsive interface with clear visual indicators for positive (green) and negative (red) financial states.

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Jinja2 Templates

## Getting Started

### Prerequisites

Make sure you have Python 3 installed on your system. 

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd CashFlow
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**:
   The SQLite database (`cashflow.db`) is automatically initialized using the `cashflow_sql.py` / `cashflow_db.py` services when needed, or you can run the provided scripts to set up the tables.

5. **Run the application**:
   ```bash
   python app.py
   ```
   *(Alternatively, run `flask run` if your environment is set up for it).*

6. **Open in Browser**:
   Navigate to `http://127.0.0.1:5000` to start managing your cash flow!

## Project Structure

- `app.py`: Main Flask application handling routing and server logic.
- `cashflow_db.py` / `cashflow_sql.py`: Database interaction and query services.
- `services/`: Contains business logic, including `analysis_service.py` for calculations and forecasting.
- `templates/`: HTML templates for the frontend UI.
- `static/`: Static assets (CSS, JS, Images).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
