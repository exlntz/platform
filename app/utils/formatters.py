import re

def format_answer(text: str) -> str:

    if not text:
        return ''

    text = text.lower().strip()

    if any(char.isdigit() for char in text):
        text = text.replace(',','.')

    text = text.replace('ё','е')

    text = re.sub(r'\s+', ' ', text)

    return text.strip()
