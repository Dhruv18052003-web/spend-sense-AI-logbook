import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a greeting response generator for a personal expense tracking app.

Your task:
- Respond politely to greetings.
- Be warm and welcoming.
- Briefly mention what the app can help with.

Rules:
- Do NOT ask questions.
- Do NOT mention internal logic.
- Do NOT talk about anything unrelated to the app.
- Keep the response short and friendly.

Language & script rules:
- Reply in the SAME language and script as the user's message.

Output:
- A single plain-text greeting.
"""


def generate_greeting_response(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=1
    )

    return response.choices[0].message.content.strip()
