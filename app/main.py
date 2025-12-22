#uvicorn app.main:app --reload запуск приложения, запускать строго из case
#можно также запустить просто main.py
#вся документация тут http://127.0.0.1:8000/docs либо http://127.0.0.1:8000/redoc
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
import uvicorn
from contextlib import asynccontextmanager
from app.database import engine,Model,SessionDep
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    print('База данных готова')
    yield
    print('Выключение сервера')

app=FastAPI(title='Платформа для подготовки к олимпиадам',version='666.666.666',lifespan=lifespan)

app.include_router(auth_router)
app.include_router(tasks_router)


data={
    'id': 1,
    'name': 'John',
    'mail': 'aomosm@mail.ru',
    'bio': None,
    'elo': 1000
}
class UserSchema(BaseModel):
    id: int
    name: str = Field(min_length=2,max_length=50)
    mail: EmailStr
    bio: str | None
    elo: int = Field(ge=0)

@app.get('/')
async def home() -> str:
    return 'главная страница'

users=[]
@app.post('/users',tags=['Пользователи'],summary='Создание пользователя')
async def create_user(user: UserSchema,session: SessionDep):
    users.append(user)
    return 'True'




if __name__=='__main__':
    uvicorn.run('app.main:app',reload=True)