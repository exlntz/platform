import math
from app.core.database import new_session
from sqlalchemy import update
from app.core.models import UserModel

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

    return rating_change


# увеличивает/уменьшает elo пользователю и возвращает получившееся значение
async def change_elo(
    user_id: int,
    elochange: float
) -> float:
    async with new_session() as session:
        query=update(UserModel).where(UserModel.id == user_id).values(rating=UserModel.rating + elochange).returning(UserModel.rating)
        result = await session.execute(query)
        new_elo = result.scalar_one()
        await session.commit()
        return new_elo