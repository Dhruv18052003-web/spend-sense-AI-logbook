import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are an intent classification engine for a household money assistant.

Your job is to classify the user's message into EXACTLY ONE of the following intents:

1. log_expense
   - The user is talking about spending money.
   - Examples: "Chips 50", "Auto 120", "Bijli bill 1800"

2. add_money
   - The user is talking about receiving or adding money.
   - Examples: "Salary aayi 25000", "Papa ne 500 diye", "Cash mila 1000", "I have 500 rs more to spend"

3. query_analysis
   - The user is asking a question or requesting information.
   - Examples: "Last month food ka kharcha?", "Kitna paisa bacha hai?", "How much did i spend today?"

4. Greetings 
    - The user is greeting you in the message. 
    - Examples: "Hii/hello", "Ram Ram", "Kaise ho", "Jai shree Krishna" 
    
5. chitchat 
    - chitchat → anything else (general questions, off-topic) 
    - Examples: "What is the capital of Australia?", "India me elections kab hai?", "What is AI?"

Rules:
- Respond with ONLY valid JSON.
- Do NOT include explanations.
- Do NOT include extra text.
- Output must contain exactly one key: "intent".

Output format:
{{
  "intent": "<one_of_the_five_intents>"
}}
"""

ALLOWED_INTENTS = {
    "log_expense",
    "add_money",
    "query_analysis",
    "greetings",
    "greeting",
    "chitchat",
}


def classify_intent(user_message: str) -> dict:
    """
    Classifies user intent using LLM.

    Returns:
    {
        "intent": "log_expense" | "add_money" | "query_analysis"
    }
    """

    print("[IntentClassifier] user_message:", user_message)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=1
    )

    raw_output = response.choices[0].message.content.strip()
    print("[IntentClassifier] raw_output:", raw_output)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        print("[IntentClassifier] parse_failed -> fallback query_analysis")
        # Fallback: if model breaks JSON, treat as query
        return {"intent": "query_analysis"}

    intent = str(parsed.get("intent", "")).strip().lower()

    if intent not in ALLOWED_INTENTS:
        print("[IntentClassifier] invalid_intent -> fallback query_analysis:", intent)
        # Safety fallback
        return {"intent": "query_analysis"}

    if intent == "greeting":
        intent = "greetings"

    print("[IntentClassifier] final_intent:", intent)
    return {"intent": intent}

