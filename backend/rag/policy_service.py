from pathlib import Path
import re


def extract_approval_threshold(text: str):

    pattern = r"(?:above|over|exceeding)\s*[₹Rs\.\s]*([\d,]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return None

    amount = match.group(1)

    amount = amount.replace(",", "")

    return float(amount)


def get_approval_threshold():

    policy_path = Path("rag/knowledge/company_policy.txt")

    policy_text = policy_path.read_text(encoding="utf-8")

    return extract_approval_threshold(policy_text)