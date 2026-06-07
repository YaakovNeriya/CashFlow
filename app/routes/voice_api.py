from flask import Blueprint, request, jsonify
from datetime import date

from app.db import add_transaction, add_recurring
from app.services.voice_service import parse_voice_text

voice_api_bp = Blueprint('voice_api', __name__)

# The groq_client is set during app initialization
groq_client = None


def init_voice_api(client):
    """Initialize the voice API with a Groq client instance."""
    global groq_client
    groq_client = client


@voice_api_bp.route('/api/voice_transaction', methods=['POST'])
def voice_transaction():
    if not groq_client:
        return jsonify({"error": "Groq API key is missing. Please configure GROQ_API_KEY in the server."}), 500

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        today = date.today()
        transactions = parse_voice_text(groq_client, text)

        added_count = 0
        for tx in transactions:
            description = tx.get('description', 'פעולה קולית')
            amount = float(tx.get('amount', 0.0))
            is_recurring = tx.get('is_recurring', False)
            
            if is_recurring:
                day_val = tx.get('day_of_month', today.day)
                try:
                    day_val = int(day_val)
                    if not (1 <= day_val <= 31):
                        day_val = today.day
                except:
                    day_val = today.day
                add_recurring(day_val, description, amount)
            else:
                date_str = tx.get('date', today.strftime('%Y-%m-%d'))
                add_transaction(date_str, description, amount)
                
            added_count += 1

        return jsonify({"success": True, "added": added_count, "transactions": transactions})

    except Exception as e:
        print(f"Error parsing voice transaction: {e}")
        return jsonify({"error": str(e)}), 500
