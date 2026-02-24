import json

from openai import OpenAI
from semantic.models import semanticConcept as SemanticConcept

client = OpenAI()


def expand_semantic_scope(base_semantic_id: str) -> list:
    """
    Expands a broad semantic_id into related semantic_ids.

    Returns:
        List of semantic_ids (strings)
    """

    system_prompt = """
        You are a semantic expansion engine for a household expense system.

        Your task:
        Given:
        - A base semantic_id
        - A list of all available semantic_ids in the database

        Decide which semantic_ids should be included when the user makes a broad query.

        Rules:
        - Only select from the provided semantic_ids.
        - Do NOT invent new semantic_ids.
        - If the base semantic is general (like "food"), include all relevant related semantic_ids.
        - If no related categories exist, return only the base semantic_id.
        - Respond with ONLY valid JSON.
        - No explanations.
        - No extra text.

        Output format:
        {{
        "expanded_semantic_ids": ["semantic_id_1", "semantic_id_2", ...]
        }}
        """

    print("[SemanticExpansionAgent] base_semantic_id:", base_semantic_id)

    all_semantics = list(
        SemanticConcept.objects.values_list("semantic_id", flat=True)
    )
    print("[SemanticExpansionAgent] available_semantic_count:", len(all_semantics))

    user_payload = {
        "base_semantic_id": base_semantic_id,
        "available_semantic_ids": all_semantics,
    }

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        temperature=1,
    )

    raw_output = response.choices[0].message.content.strip()
    print("[SemanticExpansionAgent] raw_output:", raw_output)

    try:
        parsed = json.loads(raw_output)
        expanded = parsed.get("expanded_semantic_ids")
        print("[SemanticExpansionAgent] parsed_expanded_ids:", expanded)

        if isinstance(expanded, list):
            valid = [sid for sid in expanded if sid in all_semantics]

            if base_semantic_id not in valid:
                valid.append(base_semantic_id)

            print("[SemanticExpansionAgent] valid_expanded_ids:", valid)
            return valid

    except json.JSONDecodeError:
        print("[SemanticExpansionAgent] parse_failed")

    print("[SemanticExpansionAgent] fallback_ids:", [base_semantic_id])
    return [base_semantic_id]
