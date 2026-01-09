from fastapi import APIRouter,HTTPException,status,Depends
from typing import Annotated
from sqlalchemy import select, exists
from app.core.database import SessionDep
from app.core.models import TaskModel, AttemptModel,UserModel
from app.schemas.task import TaskRead, AnswerCheckRequest, AnswerCheckResponse
from app.core.dependencies import get_current_user
from app.core.models import DifficultyLevel
from app.utils.levels import rewards

router=APIRouter(prefix='/tasks',tags=['Задачи'])

@router.get('/',summary='Получить все задачи',description='Возвращает задачи в соответствии с фильтрами')
async def get_tasks(
        session: SessionDep,
        subject: str | None = None,
        difficulty: DifficultyLevel | None = None

) -> list[TaskRead]:
    query= select(TaskModel)

    if subject:
        query=query.where(TaskModel.subject == subject)

    if difficulty:
        query=query.where(TaskModel.difficulty == difficulty)

    result = await session.execute(query) # ответ от бд, ждем ответа

    tasks = result.scalars().all() # Здесь мы получаем [TaskModel, TaskModel...]

    return tasks # FastAPI превратит это в [TaskRead, TaskRead...]



@router.post('/{task_id}/check',summary='Проверка правильного ответа по id задачи')
async def check_task_answer(
        task_id: int,
        user_data: AnswerCheckRequest,
        session: SessionDep,
        current_user: Annotated[UserModel,Depends(get_current_user)]
) -> AnswerCheckResponse:

    task = await session.get(TaskModel, task_id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Задача не найдена')

    is_correct = task.correct_answer.strip().lower() == user_data.answer.strip().lower()

    already_solved_query = select(exists().where(
        AttemptModel.user_id == current_user.id,
        AttemptModel.task_id == task_id,
        AttemptModel.is_correct == True
    ))
    was_solved_before = await session.scalar(already_solved_query)


    attempt = AttemptModel(
        user_id=current_user.id,
        task_id=task_id,
        user_answer=user_data.answer,
        is_correct=is_correct
    )
    session.add(attempt)

    message = 'Неверно! Попробуй еще раз.'

    if is_correct:
        message = 'Правильно!!!'

        if not was_solved_before:
            reward = rewards.get(task.difficulty)

            current_user.xp += reward

            message += f'Вы получили {reward} XP!'

    await session.commit()

    return AnswerCheckResponse(
        is_correct=is_correct,
        message=message
    )






@router.get('/{task_id}',summary='Получение задачи по ее id без ответа')
async def get_task_by_id(
        task_id: int,
        session: SessionDep
) -> TaskRead:
    query = select(TaskModel).where(TaskModel.id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Задача не найдена')

    return task


