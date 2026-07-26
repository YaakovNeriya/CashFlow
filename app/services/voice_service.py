from datetime import date
import json
from groq import Groq


def build_prompt(text, today=None):
    """Build the LLM prompt for extracting transactions from Hebrew text."""
    if today is None:
        today = date.today()
    
    today_str = today.strftime('%Y-%m-%d')
    day_name_en = today.strftime('%A')
    
    # Map English day to Hebrew for better LLM context
    hebrew_days = {
        'Sunday': 'ראשון', 'Monday': 'שני', 'Tuesday': 'שלישי',
        'Wednesday': 'רביעי', 'Thursday': 'חמישי', 'Friday': 'שישי', 'Saturday': 'שבת'
    }
    day_name_he = hebrew_days.get(day_name_en, '')

    prompt = f"""You are an expert financial transaction extractor for an Israeli app.
Extract all distinct financial transactions from the user's input in Hebrew.
Today's date is: {today_str} (יום {day_name_he}), and today's day of the month is {today.day}.

Rules:
1. Return ONLY a valid JSON array of objects. No markdown, no backticks, just the raw JSON array.
2. Expenses/purchases → negative amount. Income/deposits → positive amount.
3. Provide a short, clean noun-based description in Hebrew. Do NOT include the amount, .
4. For one-time transactions, provide "date" in YYYY-MM-DD format (calculate relative dates based on today).
5. For recurring/monthly transactions (פעולה קבועה / הוראת קבע / כל חודש):
   - Set "is_recurring" to true.
   - Extract or calculate the "day_of_month" (1-31). Pay special attention to Hebrew ordinal numbers for days of the month (e.g., "ראשון לחודש" = 1, "שני לחודש" = 2, "חמישי לחודש" = 5, "עשירי לחודש" = 10).
   - CRITICAL: If the input uses relative time like "ממחר" (tomorrow) or "עוד יומיים", you MUST calculate the correct day of the month mathematically relative to today ({today.day}).
   - Only if no day or relative timeframe is specified at all, use {today.day}.

Example output:
[
  {{"date": "2023-10-25", "description": "קניית קפה", "amount": -20.0, "is_recurring": false}},
  {{"description": "ביטוח", "amount": -150.0, "is_recurring": true, "day_of_month": 10}}
]

User Input: {text}"""
    
    return prompt 


def clean_llm_response(response_text):
    """Clean up possible markdown fences from LLM response."""
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    return response_text.strip() 


def parse_voice_text(groq_client, text):
    """Parse voice text using Groq LLM and return structured transactions.
    
    Returns:
        list[dict]: List of parsed transaction dictionaries
    Raises:
        Exception: If LLM call or JSON parsing fails
    """
    today = date.today()
    prompt = build_prompt(text, today)
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1024,
    )
    response_text = response.choices[0].message.content.strip()
    response_text = clean_llm_response(response_text)
    
    return json.loads(response_text)
