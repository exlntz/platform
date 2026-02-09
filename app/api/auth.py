from fastapi import APIRouter,HTTPException,status,Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Annotated

from app.core.database import SessionDep
from app.core.models import UserModel
from app.core.security import get_password_hash, is_password_correct, create_access_token, create_refresh_token, \
    verify_refresh_token
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
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ваш аккаунт заблокирован за нарушение правил."
        )

    token_payload={"sub": str(user.id)}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='Bearer'
    )


@router.post('/refresh', summary='Обновление токена')
async def refresh_token_endpoint(
        session: SessionDep,
        refresh_token: str = Body(..., embed=True)
) -> Token:

    user_id = verify_refresh_token(refresh_token)
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    payload = {"sub": str(user.id)}
    new_access_token = create_access_token(payload)
    new_refresh_token = create_refresh_token(payload)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type='bearer'
    )
