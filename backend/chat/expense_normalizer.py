from datetime import date, datetime

def normalize_expense(extracted: dict) -> dict:
    """
    Fixes and normalizes extracted expense data.

    Rules:
    - If spent_at is None → set to today
    - amount must not be None
    - raw_label must not be None
    """

    if extracted["raw_label"] is None:
        raise ValueError("Expense item not understood")

    if extracted["amount"] is None:
        raise ValueError("Expense amount not understood")

    #THIS IS THE FIX YOU KEPT ASKING FOR
    if extracted["spent_at"] is None:
        spent_at = date.today()
    else:
        # convert YYYY-MM-DD string to date object
        spent_at = datetime.strptime(
            extracted["spent_at"], "%Y-%m-%d"
        ).date()

    return {
        "raw_label": extracted["raw_label"],
        "amount": extracted["amount"],
        "spent_at": spent_at
    }
