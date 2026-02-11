from typing import Annotated
from fastapi import Depends,HTTPException,status
import jwt
from app.core.database import SessionDep
from app.core.models import UserModel
from app.core.security import oauth2_scheme
from sqlalchemy import select
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


async def get_current_user(
        session: SessionDep,
        token: Annotated[str, Depends(oauth2_scheme)]
) -> UserModel:

    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Некорректный токен или время сессии истекло',
        headers={"WWW-Authenticate": "Bearer"},  # Помогает браузеру понять тип авторизации
    )

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        user_id: int | None = payload.get('sub')

        if user_id is None:
            raise unauthorized_error
    except:
        raise unauthorized_error

    query=select(UserModel).where(UserModel.id == int(user_id))
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise unauthorized_error

    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Ваш аккаунт заблокирован.')

    return user


async def validate_admin_access(
        current_user: Annotated[UserModel,Depends(get_current_user)]
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав.'
        )
    return current_user


UserDep = Annotated[UserModel, Depends(get_current_user)]

AdminDep = Annotated[UserModel, Depends(validate_admin_access)]