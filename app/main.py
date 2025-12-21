#uvicorn main:app --reload запуск приложения, перед этим нужно быть в папке app -> cd app в терминале
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
import uvicorn
from contextlib import asynccontextmanager
from database import engine,Model,SessionDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    print('База данных готова')
    yield
    print('Выключение сервера')

app=FastAPI(title='Платформа для подготовки к олимпиадам',version='666.666.666',lifespan=lifespan)



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

fake_tasks_db = [
    {"task_name": "Task 1"},
    {"task_name": "Task 2"},
    {"task_name": "Task 3"},
    {"task_name": "Task 4"},
    {"task_name": "Task 5"},
    {"task_name": "Task 6"},
    {"task_name": "Task 7"},
    {"task_name": "Task 8"},
    {"task_name": "Task 9"},
    {"task_name": "Task 10"},
]

@app.get("/tasks")
async def get_tasks(limit: int = 10, offset: int = 0):
    return fake_tasks_db[offset : offset + limit]


if __name__=='__main__':
    uvicorn.run('app.main:app',reload=True)