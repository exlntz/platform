from fastapi import APIRouter
from sqlalchemy import select
from app.database import SessionDep
from app.models import TaskModel
from app.schemas.task import TaskRead,TaskCreate

router=APIRouter(prefix='/tasks',tags=['Задачи'])

@router.get('/')
async def get_tasks(
        session: SessionDep,
        subject: str | None = None,
        difficulty: str | None = None

) -> list[TaskRead]:
    query= select(TaskModel)

    if subject:
        query=query.where(TaskModel.subject == subject)

    if difficulty:
        query=query.where(TaskModel.difficulty == difficulty)

    result = await session.execute(query) # ответ от бд, ждем ответа

    tasks = result.scalars().all() # Здесь мы получаем [TaskModel, TaskModel...]

    return tasks # FastAPI превратит это в [TaskRead, TaskRead...]

@router.post('/')
async def create_task(
        new_task:TaskCreate,
        session:SessionDep
) -> TaskRead:
    task_db=TaskModel(
        title=new_task.title,
        description=new_task.description,
        subject=new_task.subject,
        theme=new_task.theme,
        difficulty=new_task.difficulty,
        correct_answer=new_task.correct_answer)

    session.add(task_db)
    await session.commit()
    await session.refresh(task_db)

    return TaskRead.model_validate(task_db)
