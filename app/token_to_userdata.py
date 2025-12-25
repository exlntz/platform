from typing import Annotated
from fastapi import Depends,HTTPException,status
import jwt
from app.database import SessionDep
from app.models import UserModel
from app.security import SECRET_KEY,ALGORITHM,oauth2_scheme
from sqlalchemy import select


async def get_current_user(
        session: SessionDep,
        token: Annotated[str, Depends(oauth2_scheme)]
) -> UserModel:

    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Некорректный токен или время сессии истекло'
    )

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        username: str | None = payload.get('sub')

        if username is None:
            raise unauthorized_error
    except:
        raise unauthorized_error

    query=select(UserModel).where(UserModel.username == username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise unauthorized_error
    return user