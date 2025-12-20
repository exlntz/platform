from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
import uvicorn

app=FastAPI()

data={
    'id': 1,
    'name': 'John',
    'mail': 'aomosm@mail.ru',
    'bio': None,
    'elo': 1000
}
class UserSchema(BaseModel):
    id: int
    name: str = Field(max_length=50)
    mail: EmailStr
    bio: str | None
    elo: int = Field(ge=0)

@app.get('/')
def home() -> str:
    return 'главная страница'

users=[]
@app.post('/users',tags=['Пользователи'],summary='Создание пользователя')
def create_user(user: UserSchema):
    users.append(user)
    return 'True'



if __name__=='__main__':
    uvicorn.run('app.main:app',reload=True)