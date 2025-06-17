import re

def extract_person_name(prompt: str) -> str | None:
    match = re.search(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", prompt)
    return match.group(1) if match else None