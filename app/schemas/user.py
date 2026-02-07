from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict, field_validator,SecretStr
from typing import Self
from datetime import datetime
from app.core.constants import RankName, Achievement


class UserRegister(BaseModel):
    username: str = Field(...,min_length=3,max_length=40,description='Имя пользователя')
    email: EmailStr = Field(..., description='Почта')
    password: SecretStr = Field(...,min_length=8,description='Пароль')
    password_repeat: SecretStr = Field(...,min_length=8,description='Повтор пароля')

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: SecretStr) -> SecretStr:
        password = v.get_secret_value()
        if not any(char.isdigit() for char in password):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')

        return v

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password.get_secret_value() != self.password_repeat.get_secret_value():
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
    achievements: list[Achievement]
    rank: RankName
    total_attempts: int
    correct_solutions: int
    success_rate: float

    xp: int
    level: int
    xp_current: int
    xp_next: int
    progress: float
    created_at: datetime

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
    avatar_url: str | None


class EloHistoryPoint(BaseModel):
    rating: float
    change: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)