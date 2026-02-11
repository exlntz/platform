from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.pvp import router as pvp_router
from app.api.profile import router as profile_router
from app.api.leaderboard import router as leaderboard_router
from app.api.admin import router as admin_router
from app.api.constants import router as constants_router

import os
from app.core.database import new_session
from app.core.init_db import create_first_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Сайт запускается")
    async with new_session() as session:
        await create_first_superuser(session)

    print("База данных управляется через Alembic")
    yield
    print('Выключение сервера')

IS_PROD = os.getenv('VITE_IS_PROD') == 'true'
app=FastAPI(title='Платформа для подготовки к олимпиадам',
            version='1.0.0',
            lifespan=lifespan,
            root_path="/api" if IS_PROD else '',
            docs_url="/docs",
            openapi_url="/openapi.json")


os.makedirs('static/avatars',exist_ok=True)
app.mount('/static', StaticFiles(directory='static'), name='static')



origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://olymp-platform.ru",
    "https://www.olymp-platform.ru",
    "http://olymp-platform.ru"
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
app.include_router(constants_router)


@app.get('/',tags=['Система'])
async def check() -> str:
    return "Сайт запущен"


