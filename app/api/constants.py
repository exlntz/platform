from fastapi import APIRouter
from app.core.constants import Subject, Tag, DifficultyLevel, RankName, SUBJECT_TO_TAGS, Achievement

router = APIRouter(prefix='/constants', tags=['Константы'])

@router.get("/", summary='Получить все константы')
async def get_constants():
    return {
        "subjects": Subject.to_list(),
        "tags": Tag.to_list(),
        "difficulties": DifficultyLevel.to_list(),
        "ranks": RankName.to_list(),
        "constant_achievements": Achievement.to_list()
    }


@router.get("/tags_for_subject",summary='Возвращает все теги, доступные для предмета')
async def get_available_tags(subject: Subject | None = None):

    if subject and subject in SUBJECT_TO_TAGS:
        tags_list = SUBJECT_TO_TAGS[subject]
        return [
            {
                "key": t.value,
                "label": t.label,
            }
            for t in tags_list
        ]

    return Tag.to_list()