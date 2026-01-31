from fastapi import APIRouter, UploadFile, File, HTTPException,status
from sqlalchemy import select, func, or_
from app.core.database import SessionDep
from app.core.models import AttemptModel, TaskModel
from app.core.dependencies import UserDep
from app.schemas.user import FullProfileResponse, UserProfile, UserStats, SubjectStat
import shutil
import uuid

ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg'}

router = APIRouter(prefix='/profile',tags=['Профиль'])

@router.get('/',summary='Профиль пользователя',description='Возвращает данные пользователя и его статистику в одном структурированном ответе.')
async def get_full_profile(
        session: SessionDep,
        current_user: UserDep
) -> FullProfileResponse:

    user_data = UserProfile(
        username=current_user.username,
        email = current_user.email,
        rating=round(current_user.rating,1),
        created_at=current_user.created_at,
        avatar_url=current_user.avatar_url
    )

    query = select(
        func.count(AttemptModel.id).label('total'),
        func.count(func.distinct(AttemptModel.task_id)).filter(AttemptModel.is_correct == True).label('unique_correct')
    ).where(AttemptModel.user_id == current_user.id)

    result = await session.execute(query)
    stats = result.one()

    total = stats.total or 0
    unique_solved = stats.unique_correct or 0

    success_rate=round((unique_solved/total*100),1) if total>0 else 0.0

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
            func.count(func.distinct(AttemptModel.task_id)).filter(AttemptModel.is_correct == True).label('correct_count')
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

        subject_breakdown.append(SubjectStat(
            subject=row.subject,
            avg_speed=round(float(row.avg_speed or 0), 2),
            success_rate=round((subj_correct / subj_attempts * 100), 1) if subj_attempts > 0 else 0.0,
            total_solved=subj_correct
        ))

    stats_data = UserStats(
        total_attempts=total,
        correct_solutions=unique_solved,
        success_rate=success_rate,
        subject_stats=subject_breakdown,
        message='Данные успешно получены'
    )

    return FullProfileResponse(
        user=user_data,
        stats=stats_data
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
    await session.commit()

    return {'url': generated_url}

