import json
from datetime import date
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a query extraction engine for a personal finance app.

Today’s date is: {CURRENT_DATE}

Your ONLY task is to convert the user’s question into a structured query description.
You must NOT answer the question.

The app only supports questions about past spending.

You must extract:
1. query_type:
   - "aggregate" → user wants a total / sum
   - "list" → user wants a list of expenses
   - "boolean" → user wants a yes/no answer

2. metric:
   - "total_spent" → sum of money spent
   - "spent_any" → whether any spending happened

3. semantic_concept:
   - category of spending like "food", "rent", "alcohol"
   - null if not specified

4. time_range:
   - type: one of ["today", "yesterday", "this_month", "last_month", "last_n_days"]
   - value: number ONLY if type is "last_n_days", otherwise null

Rules:
- Do NOT guess missing information.
- Do NOT compute dates.
- Do NOT access databases.
- Do NOT explain anything.
- Do NOT behave like a chatbot.
- Respond with ONLY valid JSON.
- No extra text.

Output format:
{{
  "query_type": "<aggregate|list|boolean>",
  "metric": "<total_spent|spent_any>",
  "semantic_concept": "<string_or_null>",
  "time_range": {{
    "type": "<string>",
    "value": <number_or_null>
  }}
}}
"""


def extract_query(user_message: str) -> dict:
    """
    Extracts structured query intent from user message.

    Returns:
    {
        "query_type": str,
        "metric": str,
        "semantic_concept": str | None,
        "time_range": {
            "type": str,
            "value": int | None
        }
    }
    """

    prompt = SYSTEM_PROMPT.format(
        CURRENT_DATE=date.today().isoformat()
    )

    print("[QueryExtractor] user_message:", user_message)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=1
    )

    raw_output = response.choices[0].message.content.strip()
    print("[QueryExtractor] raw_output:", raw_output)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        print("[QueryExtractor] parse_failed -> fallback unsupported query")
        # Safe fallback: treat as unsupported query
        return {
            "query_type": None,
            "metric": None,
            "semantic_concept": None,
            "time_range": None
        }

    result = {
        "query_type": parsed.get("query_type"),
        "metric": parsed.get("metric"),
        "semantic_concept": parsed.get("semantic_concept"),
        "time_range": parsed.get("time_range"),
    }
    print("[QueryExtractor] parsed_result:", result)
    return result
