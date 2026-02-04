from fastapi import APIRouter, UploadFile, File, HTTPException,status
from sqlalchemy import select, func, or_, distinct
from app.core.database import SessionDep
from app.core.models import AttemptModel, TaskModel, EloHistoryModel
from app.core.dependencies import UserDep
from app.schemas.user import SubjectStats,UserStatsResponse,UserProfileRead
import shutil
import uuid
from app.schemas.user import EloHistoryPoint
from app.utils.achievments import check_and_award_achievement

from app.utils.levels import calculate_level_info

ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg'}

router = APIRouter(prefix='/profile',tags=['Профиль'])

@router.get('/',summary='Профиль пользователя',description='Возвращает данные пользователя и его статистику в одном структурированном ответе.')
async def get_my_profile(
        session: SessionDep,
        current_user: UserDep
) -> UserProfileRead:

    level_data = calculate_level_info(current_user.xp)

    first_success_subquery = (
        select(
            AttemptModel.task_id,
            func.min(AttemptModel.created_at).label('first_correct_at')
        )
        .where(
            AttemptModel.user_id == current_user.id,
            AttemptModel.is_correct == True
        )
        .group_by(AttemptModel.task_id)
        .subquery()
    )

    query = (
        select(
            func.count(AttemptModel.id).label('total'),
            func.count(distinct(AttemptModel.task_id)).filter(AttemptModel.is_correct == True).label('unique_solved')
        )
        .outerjoin(first_success_subquery, AttemptModel.task_id == first_success_subquery.c.task_id)
        .where(
            AttemptModel.user_id == current_user.id,
            or_(
                first_success_subquery.c.first_correct_at == None,  # Задача еще не решена
                AttemptModel.created_at <= first_success_subquery.c.first_correct_at  # Попытки до успеха
            )
        )
    )

    result = await session.execute(query)
    stats = result.one()

    total = stats.total or 0
    unique_solved = stats.unique_solved or 0

    success_rate=round((unique_solved/total*100),1) if total>0 else 0.0

    return UserProfileRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        rating=round(current_user.rating,1),
        avatar_url=current_user.avatar_url,

        total_attempts=total,
        correct_solutions=unique_solved,
        success_rate=success_rate,

        xp=current_user.xp,
        level=level_data['level'],
        xp_current=level_data['xp_current'],
        xp_next=level_data['xp_next'],
        progress=level_data['progress'],

    )


@router.post('/avatar',summary='Загрузить аватарку')
async def upload_avatar(
        session: SessionDep,
        current_user: UserDep,
        file: UploadFile = File(...)
):

    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_AVATAR_EXTENSIONS or '.' not in file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f'Недопустимое расширение файла')

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Файл должен быть изображением')

    file_path = f'static/avatars/user_{current_user.id}_{uuid.uuid4().hex}.{ext}'

    with open(file_path,'wb') as buffer:
        shutil.copyfileobj(file.file, buffer) #type: ignore

    generated_url = f'/{file_path}'

    current_user.avatar_url = generated_url
    session.add(current_user)

    new_badges = await check_and_award_achievement(current_user, session)

    await session.commit()

    return {'url': generated_url,
            'new_achievements': new_badges,
    }


@router.get('/stats', summary='Детальная статистика по предметам')
async def get_user_stats(
        current_user: UserDep,
        session: SessionDep,
) -> UserStatsResponse:

    first_success_subquery = (
        select(
            AttemptModel.task_id,
            func.min(AttemptModel.created_at).label('first_correct_at')
        )
        .where(
            AttemptModel.user_id == current_user.id,
            AttemptModel.is_correct == True
        )
        .group_by(AttemptModel.task_id)
        .subquery()
    )

    subject_query = (
        select(
            TaskModel.subject,
            func.avg(AttemptModel.time_spent).filter(AttemptModel.is_correct == True).label('avg_speed'),
            func.count(AttemptModel.id).label('attempts_count'),
            func.count(func.distinct(AttemptModel.task_id)).filter(AttemptModel.is_correct == True).label(
                'correct_count')
        )
        .join(AttemptModel, TaskModel.id == AttemptModel.task_id)
        .outerjoin(first_success_subquery, AttemptModel.task_id == first_success_subquery.c.task_id)
        .where(
            AttemptModel.user_id == current_user.id,
            or_(
                first_success_subquery.c.first_correct_at == None,
                AttemptModel.created_at <= first_success_subquery.c.first_correct_at
            )
        )
        .group_by(TaskModel.subject)
    )

    subject_res = await session.execute(subject_query)
    subject_rows = subject_res.all()

    subject_breakdown = []

    for row in subject_rows:
        subj_attempts = row.attempts_count or 0
        subj_correct = row.correct_count or 0

        accuracy = round((subj_correct / subj_attempts * 100), 1) if subj_attempts > 0 else 0.0

        avg_time = round(float(row.avg_speed), 1) if row.avg_speed else 0.0

        subject_breakdown.append(SubjectStats(
            subject=row.subject,
            total_attempts=subj_attempts,
            correct_count=subj_correct,
            accuracy_percent=accuracy,
            average_time=avg_time
        ))

    return UserStatsResponse(stats=subject_breakdown)


@router.get('/elo_history',summary='История рейтинга для графика в профиле')
async def get_elo_history(
    session: SessionDep,
    current_user: UserDep
) -> list[EloHistoryPoint]:

    query = (
        select(EloHistoryModel)
        .where(EloHistoryModel.user_id == current_user.id)
        .order_by(EloHistoryModel.created_at.asc())
    )

    result = await session.execute(query)
    history = result.scalars().all()

    return history