from fastapi import APIRouter
from app.core.database import SessionDep
from sqlalchemy import select
from app.core.models import UserModel
from app.schemas.user import LeaderboardPlayer
from app.utils.levels import calculate_level_info

router = APIRouter(prefix='/leaderboard',tags=['Таблица лидеров'])

@router.get('/',summary='Таблица лидеров',description='Вывод первых 10 пользователей с наибольшим рейтингом')
async def get_leaderboard(
        session: SessionDep,
        limit: int = 10
) -> list[LeaderboardPlayer]:
    query=select(UserModel).order_by(UserModel.rating.desc()).limit(limit)
    result = await session.execute(query)
    users=result.scalars().all() #список кортежей - 3 обьекта LeaderboardPlayer - список LeaderboardPlayer

    response_list =[]

    for user in users:
        level = calculate_level_info(user.xp)['level']

        data=LeaderboardPlayer(
            username=user.username,
            rating=user.rating,
            level=level,
        )
        response_list.append(data)

    return response_list # список LeaderboardPlayer моделей
