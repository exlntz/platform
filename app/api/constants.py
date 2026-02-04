from fastapi import APIRouter
from app.core.constants import Subject, Tag, DifficultyLevel, RankName

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