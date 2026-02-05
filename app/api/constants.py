from fastapi import APIRouter
from app.core.constants import Subject, Tag, DifficultyLevel, RankName, SUBJECT_TO_TAGS

router = APIRouter(prefix='/constants', tags=['Константы'])

@router.get("/", summary='Получить все константы')
async def get_constants():
    return {
        "subjects": [
            {"key": s.value, "label": s.label} for s in Subject
        ],
        "tags": [
            {"key": t.value, "label": t.label} for t in Tag
        ],
        "difficulty": [
            {"key": d.value, "label": d.value} for d in DifficultyLevel
        ],
        "ranks": [
            {"key": r.value, "label": r.label} for r in RankName
        ]
    }


@router.get("/tags_for_subject",summary='Возвращает все теги, доступные для предмета')
async def get_available_tags(subject: Subject | None = None):

    if subject and subject in SUBJECT_TO_TAGS:
        return SUBJECT_TO_TAGS[subject]

    return list(Tag)