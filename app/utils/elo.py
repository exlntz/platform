import math
from app.core.database import new_session
from app.core.models import UserModel
from app.core.constants import RankName
from fastapi import status, HTTPException
WIN = 1.0
DRAW = 0.5
LOSS = 0.0

def calculate_elo_change(
        player_rating: float,
        opponent_rating: float,
        match_result: float,
        k: int = 32
) -> float:
    diff = (opponent_rating - player_rating) / 400

    E = 1 / (1 + math.pow(10,diff))

    rating_change = k * (match_result - E)

    return round(float(rating_change),1)


# увеличивает/уменьшает elo пользователю и возвращает получившееся значение
async def change_elo(
    user_id: int,
    elochange: float
) -> float:
    async with new_session() as session:
        user = await session.get(UserModel, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Пользователь не найден")

        user.rating = round(float(user.rating + elochange), 1)
        new_rank = get_rank_by_elo(user.rating)
        user.user_rank = new_rank
        await session.commit()
        return user.rating


def get_rank_by_elo(elo: float) -> RankName:
    for rank in ELO_RANKS:
        if elo >= rank["min_elo"]:
            return rank["name"]
    return RankName.BRONZE


ELO_RANKS = [
    {"name": RankName.LEGEND, "min_elo": 5000},
    {"name": RankName.SENSEI, "min_elo": 3000},
    {"name": RankName.ELITE, "min_elo": 2300},
    {"name": RankName.GOLD, "min_elo": 1700},
    {"name": RankName.SILVER, "min_elo": 1200},
    {"name": RankName.BRONZE, "min_elo": 0},

]

