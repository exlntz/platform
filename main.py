#uvicorn app.main:app --reload запуск приложения, запускать строго из case
#можно также запустить просто main.py
#вся документация тут http://127.0.0.1:8000/docs либо http://127.0.0.1:8000/redoc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from app.database import engine,Model
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.pvp import router as pvp_router
from app.api.profile import router as profile_router
from app.api.leaderboard import router as leaderboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    print('База данных готова')
    yield
    print('Выключение сервера')

app=FastAPI(title='Платформа для подготовки к олимпиадам',version='666.666.666',lifespan=lifespan)


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



@app.get('/',tags=['главная страница'])
async def home() -> str:
    return 'главная страница'




if __name__=='__main__':
    uvicorn.run('main:app',reload=True)