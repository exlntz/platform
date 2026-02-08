from app.core.models import UserModel, AttemptModel
from app.core.constants import Achievement
from sqlalchemy import select, func,distinct
from sqlalchemy.orm.attributes import flag_modified


async def check_and_award_achievement(user: UserModel, session) -> list[str]:

    if user.all_achievements is None:
        user.all_achievements = []
    new_achievements_labels = []
    current_achievements_values = {str(a) for a in user.all_achievements}

    query = select(func.count(distinct(AttemptModel.task_id))).where(
        AttemptModel.user_id == user.id,
        AttemptModel.is_correct == True
    )
    result = await session.execute(query)
    solved_tasks_count = result.scalar() or 0

    if solved_tasks_count >= 1 and Achievement.FIRST_STEP.value not in current_achievements_values:
        user.all_achievements.append(Achievement.FIRST_STEP)
        new_achievements_labels.append(Achievement.FIRST_STEP.label)

    #Гуру
    if solved_tasks_count >= 10 and Achievement.GURU.value not in current_achievements_values:
        user.all_achievements.append(Achievement.GURU)
        new_achievements_labels.append(Achievement.GURU.label)

    #аватарка
    if user.avatar_url and Achievement.PROFILE_MASTER.value not in current_achievements_values:
        user.all_achievements.append(Achievement.PROFILE_MASTER)
        new_achievements_labels.append(Achievement.PROFILE_MASTER.label)

    if new_achievements_labels:
        flag_modified(user, "all_achievements")
        await session.flush()

    return new_achievements_labels