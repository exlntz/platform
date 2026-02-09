import re
from app.core.constants import SUBJECT_TO_TAGS, Subject, DifficultyLevel,Tag
from fastapi import HTTPException,status
def format_answer(text: str) -> str:

    if not text:
        return ''

    text = text.lower().strip()

    if any(char.isdigit() for char in text):
        text = text.replace(',','.')

    text = text.replace('ё','е')

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def validate_task_data(row_index: int, item: dict):
    title = item.get("title")
    if not title:
        return None

    raw_subject = item.get("subject", "").strip().upper()
    try:
        subject_enum = Subject(raw_subject)
    except ValueError:
        allowed_subjects = ", ".join([s.value for s in Subject])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка в строке {row_index + 1} ('{title}'): Неверный предмет '{item.get('subject')}'. Допустимые: {allowed_subjects}"
        )

    raw_difficulty = item.get("difficulty", "").strip().upper()
    try:
        difficulty_enum = DifficultyLevel(raw_difficulty)
    except ValueError:
        allowed_difficulties = ", ".join([d.value for d in DifficultyLevel])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка в строке {row_index + 1} ('{title}'): Неверная сложность '{item.get('difficulty')}'. Допустимые: {allowed_difficulties}"
        )

    raw_tags = item.get("tags", [])
    if isinstance(raw_tags, list):
        cleaned_tags = [t.strip().upper() for t in raw_tags if t.strip()]
    else:
        cleaned_tags = []

    allowed_tags_enums = SUBJECT_TO_TAGS.get(subject_enum, [])
    allowed_tag_values = {t.value for t in allowed_tags_enums}

    validated_tags = []
    for tag_str in cleaned_tags:
        try:
            tag_enum = Tag(tag_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка в строке {row_index + 1} ('{title}'): Тег '{tag_str}' не существует в системе."
            )

        if tag_enum.value not in allowed_tag_values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка в строке {row_index + 1} ('{title}'): Тег '{tag_str}' недопустим для предмета '{subject_enum.value}'"
            )
        validated_tags.append(tag_enum.value)

    return {
        "title": title,
        "description": item.get("description", ""),
        "subject": subject_enum.value,
        "tags": validated_tags,
        "hint": item.get("hint", ""),
        "difficulty": difficulty_enum.value,
        "correct_answer": item.get("correct_answer", "")
    }