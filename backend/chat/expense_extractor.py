import json
from openai import OpenAI
from datetime import date

client = OpenAI()


SYSTEM_PROMPT = f"""
You are an expense extraction engine for a household money assistant.

Today’s date is: {date.today().isoformat()}

Your ONLY task is to extract expense details from the user's message.
If the message is NOT about spending money, return null for all fields.

Extract ONLY the following fields:
- raw_label: what the money was spent on (short, lowercase, no amount)
- amount: numeric value of money spent
- spent_at:
    - Return an ISO date (YYYY-MM-DD) if a date is explicitly mentioned
    - If user says "today" / "aaj", return {date.today().isoformat()}
    - If user says "yesterday" / "kal", return the date one day before {date.today().isoformat()}
    - Return null if the user does NOT mention any date

Rules:
- Do NOT guess or assume missing information.
- Do NOT answer questions.
- Do NOT behave like a chatbot.
- Do NOT add explanations.
- Do NOT classify categories.
- Respond with ONLY valid JSON.
- No extra text.

Output format:
{{
  "raw_label": "<string_or_null>",
  "amount": <number_or_null>,
  "spent_at": "<YYYY-MM-DD_or_null>"
}}
"""


def extract_expense(user_message: str) -> dict:
    """
    Extracts expense details from user message.

    Contract:
    - spent_at is None IF user did not mention a date
    - Backend must decide default date (usually today)
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=1  # IMPORTANT: deterministic extraction
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        # Hard fail-safe: no guessing
        return {
            "raw_label": None,
            "amount": None,
            "spent_at": None
        }

    return {
        "raw_label": parsed.get("raw_label"),
        "amount": parsed.get("amount"),
        "spent_at": parsed.get("spent_at")
    }
