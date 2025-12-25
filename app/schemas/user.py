from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import Self
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated


class UserRegister(BaseModel):
    username: str = Field(...,min_length=3,max_length=40,description='Имя пользователя')
    email: EmailStr = Field(..., description='Почта')
    password: str = Field(...,min_length=6,description='Пароль')
    password_repeat: str = Field(...,min_length=6,description='Повтор пароля')

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError('Пароли не совпадают!')
        return self



class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'



class UserProfile(BaseModel):
    username: str
    email: str
    rating: float
    created_at: datetime


class UserStats(BaseModel):
    total_attempts: int
    correct_attempts: int
    success_rate: float
    message: str


class FullProfileResponse(BaseModel):
    user: UserProfile
    stats: UserStats


class LeaderboardPlayer(BaseModel):
    username: str
    rating: float