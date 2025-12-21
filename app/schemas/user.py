from pydantic import BaseModel,Field,EmailStr


class UserRegister(BaseModel):
    username: str = Field(...,min_length=2,max_length=40,description='Имя пользователя')
    password: str = Field(...,min_length=6,description='Пароль')
    email: EmailStr = Field(...,description='Почта')


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    rating: float = 1000.0
    is_admin: bool = 0