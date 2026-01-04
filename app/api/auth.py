from fastapi import APIRouter,HTTPException,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Annotated

from app.core.database import SessionDep
from app.core.models import UserModel
from app.core.security import get_password_hash,is_password_correct,create_access_token
from app.schemas.user import UserRegister,Token

router=APIRouter(prefix='/auth',tags=['Авторизация'])


@router.post('/register',summary='Регистрация')
async def register_user(new_user: UserRegister,session: SessionDep):
    hashed_pass=get_password_hash(new_user.password)

    user_db=UserModel(
        #id сам создается
        username=new_user.username,
        email=str(new_user.email),
        hashed_password=hashed_pass,
        # рейтинг = 1000, сам создается в models.py
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


@router.post('/login',summary='Логин')
async def login_user(
        session: SessionDep,
        form_data: Annotated[OAuth2PasswordRequestForm,Depends()]
) -> Token:
    query=select(UserModel).where(UserModel.username == str(form_data.username))
    result=await session.execute(query)
    user=result.scalar_one_or_none()
    if not user or not is_password_correct(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверная почта или пароль!'
        )
    token=create_access_token(data={'sub': user.username})

    return Token(access_token=token,token_type='bearer')


