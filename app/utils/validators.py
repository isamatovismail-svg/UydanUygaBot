import re

def is_valid_phone(text: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)]", "", text)
    return bool(re.fullmatch(r"(\+?998)?\d{9}", cleaned))
