from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.models import UserModel
from app.core.security import get_password_hash

async def create_first_superuser(session: AsyncSession):
    print("Проверка суперпользователя")
    try:
        query = select(UserModel).where(UserModel.username == settings.SUPERUSER)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            print(f"Создание админа:{settings.SUPERUSER}")
            new_superuser = UserModel(
                username=settings.SUPERUSER,
                hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
                is_admin=True,
                is_banned=False,
                email="superuser@superuser.com",
            )
            session.add(new_superuser)
            await session.commit()
            print("Суперпользователь успешно создан!")
        else:
            print("Суперпользователь уже существует")
    except Exception as e:
        print(f"Ошибка при создании суперпользователя: {e}")