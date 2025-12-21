from fastapi import APIRouter,HTTPException,status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import SessionDep, new_session
from app.models import UserModel
from app.security import get_password_hash
from app.schemas.user import UserRegister

router=APIRouter(prefix='/auth',tags=['Авторизация'])


@router.post('/register')
async def register_user(new_user: UserRegister,session: SessionDep):
    hashed_pass=get_password_hash(new_user.password)

    user_db=UserModel(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hashed_pass,
        rating=1000.0
    )
    try:
        session.add(user_db)
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователем с таким логином или Email уже существует'
        )
    return {"status": "ok", "message": "Регистрация прошла успешно!"}