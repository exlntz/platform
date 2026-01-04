from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select, func, Integer
from app.core.database import SessionDep
from app.core.models import UserModel, AttemptModel
from app.core.dependencies import get_current_user
from app.schemas.user import FullProfileResponse, UserProfile, UserStats
import shutil


router = APIRouter(prefix='/profile',tags=['Профиль'])

@router.get('/',summary='Профиль пользователя',description='Возвращает данные пользователя и его статистику в одном структурированном ответе.')
async def get_full_profile(
        session: SessionDep,
        current_user: Annotated[UserModel,Depends(get_current_user)]
) -> FullProfileResponse:

    user_data = UserProfile(
        username=current_user.username,
        email = current_user.email,
        rating=current_user.rating,
        created_at=current_user.created_at,
        avatar_url=current_user.avatar_url
    )

    query=select(func.count(AttemptModel.id).label('total'),
                 func.sum(AttemptModel.is_correct.cast(Integer)).label('correct')).where(
        AttemptModel.user_id == current_user.id
    )

    result = await session.execute(query)
    stats=result.one()

    total=stats.total or 0
    correct=stats.correct or 0

    unique_solved_query = select(func.count(func.distinct(AttemptModel.task_id))).where(
        AttemptModel.user_id == current_user.id,
        AttemptModel.is_correct == True
    )
    unique_solved_count = await session.scalar(unique_solved_query) or 0

    success_rate=round((unique_solved_count/total*100),1) if total>0 else 0.0

    stats_data = UserStats(
        total_attempts=total,
        correct_solutions=unique_solved_count,
        success_rate=success_rate,
        message='ПРИВЕТ!!!!!!!'
    )

    return FullProfileResponse(
        user=user_data,
        stats=stats_data
    )


@router.post('/avatar',summary='Загрузить аватарку')
async def upload_avatar(
        session: SessionDep,
        current_user: Annotated[UserModel,Depends(get_current_user)],
        file: UploadFile = File(...)
):
    file_path = f'static/avatars/user_{current_user.id}_{file.filename}'

    with open(file_path,'wb') as buffer:
        shutil.copyfileobj(file.file, buffer) #type: ignore

    generated_url = f'/{file_path}'

    current_user.avatar_url = generated_url
    session.add(current_user)
    await session.commit()

    return {'url': generated_url}

