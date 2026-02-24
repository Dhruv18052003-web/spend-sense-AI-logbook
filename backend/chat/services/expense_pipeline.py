from chat.expense_extractor import extract_expense
from chat.expense_normalizer import normalize_expense
from chat.semantic_resolver import resolve_semantic


def process_expense_message(user, user_message: str):
    """
    Orchestrates the full expense-processing pipeline.

    This function:
    - Assumes intent is log_expense
    - Extracts expense
    - Normalizes data
    - Resolves semantic concept

    Returns a dict ready for DB persistence.
    """

    #1 Extract raw expense info using LLM
    extracted = extract_expense(user_message)

    #2 Normalize (fix NULL date, validate amount/label)
    normalized = normalize_expense(extracted)

    #3 Resolve semantic concept (match or create)
    semantic_concept = resolve_semantic(
        user=user,
        raw_label=normalized["raw_label"]
    )

    #4 Return final DB-ready object
    return {
        "raw_label": normalized["raw_label"],
        "amount": normalized["amount"],
        "spent_at": normalized["spent_at"],
        "semantic_concept": semantic_concept
    }

