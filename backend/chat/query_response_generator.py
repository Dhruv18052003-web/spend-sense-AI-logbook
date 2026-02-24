import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a response generator for an expense tracking application.

Your job:
- Convert structured query results into a clear, natural language answer.

IMPORTANT RULES:
- The user is ASKING a question. No action was performed.
- Do NOT say things like:
  "Got it", "I have noted", "Saved", "Done".
- Do NOT confirm actions.
- Be factual, neutral, and informational.
- Do NOT invent data.
- Do NOT explain internal logic.
- Do NOT ask follow-up questions.
- Keep the reply short and clear.

Language & script rules:
- Reply in the SAME language and script as the user's message.
- Preserve script style (Latin / Devanagari / native scripts).

You will receive:
- user_message (original user text)
- event_data (structured query result)

Return:
- A single plain-text reply for the user.
"""


def generate_query_response(user_message: str, event_data: dict) -> str:
    """
    Generates a user-facing reply for query intents (read-only).
    """

    print("[QueryResponseGenerator] user_message:", user_message)
    print("[QueryResponseGenerator] event_data:", event_data)

    payload = {
        "user_message": user_message,
        "event_data": event_data
    }

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(payload)
            }
        ],
        temperature=1
    )

    reply = response.choices[0].message.content.strip()
    print("[QueryResponseGenerator] reply:", reply)
    return reply
