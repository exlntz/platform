from pydantic import BaseModel,Field,EmailStr


class UserRegister(BaseModel):
    username: str = Field(...,min_length=3,max_length=40,description='Имя пользователя')
    password: str = Field(...,min_length=6,description='Пароль')
    email: EmailStr = Field(...,description='Почта')


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
