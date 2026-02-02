from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict
from typing import Self
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated


class UserRegister(BaseModel):
    username: str = Field(...,min_length=3,max_length=40,description='Имя пользователя')
    email: EmailStr = Field(..., description='Почта')
    password: str = Field(...,min_length=8,description='Пароль')
    password_repeat: str = Field(...,min_length=8,description='Повтор пароля')

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError('Пароли не совпадают!')
        return self



class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'



class UserProfileRead(BaseModel):
    id: int
    username: str
    email: str
    rating: float
    avatar_url: str | None = None

    total_attempts: int
    correct_solutions: int
    success_rate: float

    xp: int
    level: int
    xp_current: int
    xp_next: int
    progress: float

    model_config = ConfigDict(from_attributes=True)



class SubjectStats(BaseModel):
    subject: str
    total_attempts: int
    correct_count: int
    accuracy_percent: float
    average_time: float



class UserStatsResponse(BaseModel):
    stats: list[SubjectStats]



class LeaderboardPlayer(BaseModel):
    username: str
    rating: float
    level: int