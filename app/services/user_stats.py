from fastapi import HTTPException,status
from sqlalchemy import select, func, or_, distinct
from app.core.constants import Achievement
from app.core.models import AttemptModel, TaskModel, EloHistoryModel, UserModel
from app.schemas.user import SubjectStats, UserStatsResponse, UserProfileRead
from app.utils.levels import calculate_level_info


async def calculate_user_stats(
        session,
        user_id: int,
):

    first_success_subquery = (
        select(
            AttemptModel.task_id,
            func.min(AttemptModel.created_at).label('first_correct_at')
        )
        .where(
            AttemptModel.user_id == user_id,
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
            AttemptModel.user_id == user_id,
            or_(
                first_success_subquery.c.first_correct_at == None,
                AttemptModel.created_at <= first_success_subquery.c.first_correct_at
            )
        )
        .group_by(TaskModel.subject)
    )

    result = await session.execute(subject_query)
    subject_rows = result.all()

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


async def calculate_elo_history(
        session,
        user_id: int,
        limit: int = 50
):

    query = (
        select(EloHistoryModel)
        .where(EloHistoryModel.user_id == user_id)
        .order_by(EloHistoryModel.created_at.asc())
        .limit(limit)
    )

    result = await session.execute(query)

    return result.scalars().all()

async def calculate_profile_info(
        session,
        user_id: int
):
    current_user : UserModel = await session.get(UserModel,user_id)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Пользователь не найден')

    level_data = calculate_level_info(current_user.xp)


    if current_user.all_achievements:
        formatted_achievements = [Achievement[ach].label for ach in current_user.all_achievements]
    else:
        formatted_achievements = []

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

    success_rate = round((unique_solved / total * 100), 1) if total > 0 else 0.0

    return UserProfileRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        rating=round(current_user.rating, 1),
        avatar_url=current_user.avatar_url,
        all_achievements=formatted_achievements,
        rank=current_user.user_rank,
        total_attempts=total,
        correct_solutions=unique_solved,
        success_rate=success_rate,

        xp=current_user.xp,
        level=level_data['level'],
        xp_current=level_data['xp_current'],
        xp_next=level_data['xp_next'],
        progress=level_data['progress'],
        created_at=current_user.created_at,

    )