import json 
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
    You are an add-money extraction engine for a personal finance app.

    Your ONLY task is to extract the amount of money RECEIVED by the user.

    Rules:
    - Extract the numeric amount of money received.
    - Support natural language (Hindi, English, mixed, any script).
    - If the amount is unclear or missing, return null.
    - Do NOT guess.
    - Do NOT infer currency.
    - Do NOT explain anything.
    - Do NOT behave like a chatbot.
    - Respond with ONLY valid JSON.
    - No extra text.

    Output format:
    {{
        "amount": <number_or_null>
    }}
"""

def add_money_extractor(user_message: str) -> dict:

    """
    Extracts received money amount from user message.

    Returns:
    {
        "amount": float | None
    }
    """

    response = client.chat.completions.create(
        model = "gpt-5-mini",

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": user_message
            }
        ],

        temperature = 1
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        return {"amount": None}
    
    amount = parsed.get("amount")

    # Safety: amount must be number or None
    if isinstance(amount, (int, float)):
        return {"amount": float(amount)}

    return {"amount": None}


