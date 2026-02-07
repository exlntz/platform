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


@router.post('/register',summary='Регистрация',status_code=status.HTTP_201_CREATED)
async def register_user(new_user: UserRegister,session: SessionDep):

    hashed_pass=get_password_hash(new_user.password.get_secret_value())

    user_db=UserModel(
        username=new_user.username,
        email=str(new_user.email),
        hashed_password=hashed_pass,
    )
    try:
        session.add(user_db)
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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
            detail='Неверное имя пользователя или пароль!',
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_payload={
        "sub": str(user.id),
        "username": user.username,
    }
    token=create_access_token(token_payload)

    return Token(access_token=token,token_type='bearer')


