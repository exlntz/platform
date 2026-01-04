#uvicorn app.main:app --reload запуск приложения, запускать строго из case
#можно также запустить просто main.py
#вся документация тут http://127.0.0.1:8000/docs либо http://127.0.0.1:8000/redoc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.pvp import router as pvp_router
from app.api.profile import router as profile_router
from app.api.leaderboard import router as leaderboard_router
from app.api.admin import router as admin_router
from fastapi.staticfiles import StaticFiles
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Теперь здесь не нужно вызывать Model.metadata.create_all
    print('Приложение запущено, база данных управляется через Alembic')
    yield
    print('Выключение сервера')

app=FastAPI(title='Платформа для подготовки к олимпиадам',version='666.666.666',lifespan=lifespan)


os.makedirs('static/avatars',exist_ok=True)
app.mount('/static',StaticFiles(directory='static'),name='static')


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(pvp_router)
app.include_router(profile_router)
app.include_router(leaderboard_router)
app.include_router(admin_router)



@app.get('/',tags=['Главная страница'])
async def home() -> str:
    return 'главная страница'


