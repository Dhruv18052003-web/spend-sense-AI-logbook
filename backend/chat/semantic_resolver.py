from semantic.models import semanticConcept
import json 
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a semantic classification engine for a household expense system.

Your task:
- Given a raw expense label and a list of existing semantic concepts,
  decide whether the label belongs to one of them.
- If none fit, propose a NEW semantic concept.

Rules:
- Prefer existing semantic concepts if reasonably related.
- Only create a new concept if none are suitable.
- Semantic IDs must be:
    - lowercase
    - snake_case
    - generic (reusable, not brand-specific)
- Do NOT be too specific.
- Do NOT include explanations.
- Respond with ONLY valid JSON.

Output format (match existing):
{{
  "action": "match",
  "semantic_id": "<existing_semantic_id>"
}}

Output format (create new):
{{
  "action": "create",
  "semantic_id": "<new_semantic_id>",
  "description": "<short description of new semantic id>"
}}
"""

def resolve_semantic(user ,raw_label:str) -> semanticConcept:

    """
    Resolves raw_label to a SemanticConcept.
    Matches existing or creates a new one if needed.
    """

    print("[SemanticResolver] raw_label:", raw_label)

    existing_semantic_concepts = list(
        semanticConcept.objects.values('semantic_id', 'description')
    )
    print("[SemanticResolver] existing_semantic_count:", len(existing_semantic_concepts))

    user_prompt = {
        "raw_label": raw_label,
        "existing_semantic_concepts": existing_semantic_concepts
    }

    response = client.chat.completions.create(
        model= 'gpt-5-mini',
        messages = [
            {
                "role": "system", 
                "content": SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content": json.dumps(user_prompt)
            }
        ],
        temperature = 1
    )

    raw_output = response.choices[0].message.content.strip()
    print("[SemanticResolver] raw_output:", raw_output)

    try:
        parsed = json.loads(raw_output)
        print("[SemanticResolver] parsed_output:", parsed)
    except Exception:
        print("[SemanticResolver] parse_failed -> fallback miscellaneous")
        return semanticConcept.objects.get(
            semantic_id="miscellaneous"
        )
    
    if parsed.get("action") == 'match':
        semantic_id = parsed.get("semantic_id")
        print("[SemanticResolver] action=match semantic_id:", semantic_id)
        return semanticConcept.objects.get(semantic_id=semantic_id)


    elif parsed.get("action") == 'create':
        semantic_id = parsed.get("semantic_id")
        description = parsed.get("description")
        print("[SemanticResolver] action=create semantic_id:", semantic_id)

        concept, _ = semanticConcept.objects.get_or_create(
            semantic_id=semantic_id,
            defaults={"description": description}
        )
        return concept

    #6 Ultimate fallback
    print("[SemanticResolver] unknown_action -> fallback miscellaneous")
    return semanticConcept.objects.get(
        semantic_id="miscellaneous"
    )





