from fastapi import APIRouter,HTTPException,status,Depends
from typing import Annotated
from sqlalchemy import select
from app.database import SessionDep
from app.models import TaskModel, AttemptModel,UserModel
from app.schemas.task import TaskRead,TaskCreate, AnswerCheckRequest, AnswerCheckResponse
from app.dependencies import get_current_user


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
        new_task: TaskCreate,
        session: SessionDep
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


@router.post('/{task_id}/check') #проверка правильного ответа
async def check_task_answer(
        task_id: int,
        user_data: AnswerCheckRequest,
        session: SessionDep,
        current_user: Annotated[UserModel,Depends(get_current_user)]
) -> AnswerCheckResponse:
    query = select(TaskModel).where(TaskModel.id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Задача не найдена')

    is_correct = task.correct_answer.strip().lower() == user_data.answer.strip().lower()

    attempt = AttemptModel(
        user_id=current_user.id,
        task_id=task_id,
        user_answer=user_data.answer,
        is_correct=is_correct
    )
    session.add(attempt)
    await session.commit()

    if is_correct:
        return AnswerCheckResponse(
            is_correct=True,
            message='Правильно!!!'
        )
    else:
        return AnswerCheckResponse(
            is_correct=False,
            message='Неверно! Попробуй еще раз.'
        )
