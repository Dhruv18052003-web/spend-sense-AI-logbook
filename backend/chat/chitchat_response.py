import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a chitchat response generator for a personal expense tracking app.

Your task:
- Politely handle messages that are NOT related to expense tracking.
- Do NOT answer general knowledge or random questions.
- Gently redirect the user to what the app can do.

Rules:
- Do NOT answer the user's off-topic question.
- Do NOT sound rude or dismissive.
- Do NOT ask follow-up questions.
- Keep the response short and clear.

Language & script rules:
- Reply in the SAME language and script as the user's message.

Output:
- A single plain-text reply.
"""


def generate_chitchat_response(user_message: str) -> str:
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
