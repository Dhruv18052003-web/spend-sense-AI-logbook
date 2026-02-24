import json
from openai import OpenAI

client = OpenAI()

def classify_query_scope(user_message: str, semantic_concept: str) -> str:
    """
    Determines whether the query is broad or specific.

    Returns:
        "specific" or "broad"
    """

    SYSTEM_PROMPT = """
    You are a query scope classification engine for a household expense system.

    Your task:
    Given the user's query and the extracted semantic concept,
    decide whether the user is asking about:

    1. specific
    - Only that exact semantic concept.
    - Example: "How much did I spend on food packaged snacks?"

    2. broad
    - The semantic concept and all related subcategories.
    - Example: "How much did I spend on food?"
    - Always consider 'food' and 'travel' as broad ones.

    Rules:
    - Respond with ONLY valid JSON.
    - No explanations.
    - No extra text.

    Output format:
    {{
    "scope": "specific" | "broad"
    }}
    """

    print("[QueryScopeAgent] user_message:", user_message)
    print("[QueryScopeAgent] semantic_concept:", semantic_concept)

    user_payload = {
        "user_query": user_message,
        "semantic_concept": semantic_concept
    }

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload)}
        ],
        temperature=1
)

    raw_output = response.choices[0].message.content.strip()
    print("[QueryScopeAgent] raw_output:", raw_output)

    try:
        parsed = json.loads(raw_output)
        scope = parsed.get("scope")
        print("[QueryScopeAgent] parsed_scope:", scope)
        if scope in {"specific", "broad"}:
            return scope
    except json.JSONDecodeError:
        print("[QueryScopeAgent] parse_failed")
        pass

    # Safe fallback
    print("[QueryScopeAgent] fallback_scope: specific")
    return "specific"
    