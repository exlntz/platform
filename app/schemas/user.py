from http.client import HTTPException

from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import Self

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


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
