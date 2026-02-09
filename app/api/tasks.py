import logging
from random import shuffle

import httpx
from fastapi import APIRouter,HTTPException,status
from sqlalchemy import select, exists, func, desc
from app.core.config import settings
from app.core.database import SessionDep
from app.core.models import TaskModel, AttemptModel, GeneratedTasksModel
from app.schemas.task import TaskRead, AnswerCheckRequest, AnswerCheckResponse, GeneratedTask
from app.core.dependencies import UserDep
from app.core.constants import DifficultyLevel, Subject, Tag
from app.schemas.task import GeneratedTaskCheckRequest
from app.utils.levels import rewards
from app.utils.formatters import format_answer
from app.utils.achievments import check_and_award_achievement
from datetime import datetime, timedelta, timezone
from app.services.ai_service import generate_task
router=APIRouter(prefix='/tasks',tags=['Задачи'])

@router.get('/',summary='Получить все задачи',description='Возвращает задачи в соответствии с фильтрами')
async def get_tasks(
        session: SessionDep,
        search: str | None = None,
        subject: Subject | None = None,
        difficulty: DifficultyLevel | None = None,
        tag: Tag | None = None

) -> list[TaskRead]:

    query= select(TaskModel)

    if subject:
        query=query.where(TaskModel.subject == subject)

    if difficulty:
        query=query.where(TaskModel.difficulty == difficulty)

    if tag:
        query=query.where(TaskModel.tags.contains([tag]))

    if search:
        words = search.strip().split()
        formatted_search = " & ".join([f"{word}:*" for word in words])

        ts_query = func.to_tsquery('russian', formatted_search)
        ts_vector = func.to_tsvector('russian', TaskModel.title + ' ' + TaskModel.description)

        query = query.where(ts_vector.op('@@')(ts_query))

    result = await session.execute(query)

    tasks = result.scalars().all()

    return tasks



@router.post('/{task_id}/check',summary='Проверка правильного ответа по id задачи')
async def check_task_answer(
        task_id: int,
        user_data: AnswerCheckRequest,
        session: SessionDep,
        current_user: UserDep
) -> AnswerCheckResponse:

    last_attempts_query = (
        select(AttemptModel)
        .where(AttemptModel.user_id == current_user.id, AttemptModel.task_id == task_id)
        .order_by(desc(AttemptModel.created_at))
        .limit(3)
    )
    result = await session.execute(last_attempts_query)
    last_attempts = result.scalars().all()

    now = datetime.now(timezone.utc)
    spam_threshold = timedelta(seconds=2)
    cooldown_duration = timedelta(seconds=10)

    if len(last_attempts) >= 3:
        gap_1 = last_attempts[0].created_at - last_attempts[1].created_at
        gap_2 = last_attempts[1].created_at - last_attempts[2].created_at
        current_gap = now - last_attempts[0].created_at
        if gap_1 < spam_threshold and gap_2 < spam_threshold:
            if current_gap < cooldown_duration:
                seconds_left = int((cooldown_duration - current_gap).total_seconds())
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Слишком много попыток! Подождите {seconds_left} сек."
                )
    new_badges = []
    task = await session.get(TaskModel, task_id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Задача не найдена')

    correct_format_answer = format_answer(str(task.correct_answer))
    user_format_answer = format_answer(user_data.answer)
    is_correct = (correct_format_answer == user_format_answer)

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
        is_correct=is_correct,
        time_spent=user_data.time_spent
    )
    session.add(attempt)
    await session.flush()
    message = 'Неверно! Попробуй еще раз.'

    if is_correct:
        message = 'Правильно!!!'

        new_badges = await check_and_award_achievement(current_user, session)
        
        if not was_solved_before:
            reward = rewards.get(task.difficulty)

            current_user.xp += reward

            message += f'Вы получили {reward} XP!'

    await session.commit()

    return AnswerCheckResponse(
        is_correct=is_correct,
        message=message,
        achievements=new_badges
    )


KEY_1 = settings.GROQ_API_KEY_1
KEY_2 = settings.GROQ_API_KEY_2
KEY_3 = settings.GROQ_API_KEY_3

keys_list = [KEY_1, KEY_2, KEY_3]

models_list = ['openai/gpt-oss-120b', 'llama-3.3-70b-versatile', 'meta-llama/llama-4-maverick-17b-128e-instruct',
       'meta-llama/llama-4-scout-17b-16e-instruct']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

allowed_tags = [t.value for t in Tag]

@router.get('/generate',summary='Генерирует задачу по заданным параметрам')
async def generate_task_for_user(
        subject: Subject,
        difficulty: DifficultyLevel,
        session: SessionDep,
        user: UserDep
):
    generated_data: GeneratedTask | None = None  # Сюда положим результат
    success = False
    shuffle(keys_list)

    for key in keys_list:
        if success: break
        for model in models_list:
            if success: break
            for attempt in range(3):
                try:
                    generated_data = await generate_task(
                            subject=subject,
                            difficulty=difficulty,
                            api_key=key,
                            model=model,
                            allowed_tags=allowed_tags)
                    success = True
                    break
                except (httpx.ConnectError, httpx.ProxyError) as e:
                    logger.warning(f"Проблема с прокси на модели {model}, ключ {key}: {e}")
                    continue
                except Exception as e:
                    logger.error(f'ошибка модели {model}, ключ {key}, ошибка {e}')
                    continue

    if not success or not generated_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Не удалось сгенерировать задачу. ИИ отдыхает"
        )

    query = select(GeneratedTasksModel).where(GeneratedTasksModel.user_id == user.id)
    result = await session.execute(query)
    existing_task = result.scalar_one_or_none()

    task_dict = generated_data.model_dump()

    if existing_task:
        for key, value in task_dict.items():
            if hasattr(existing_task, key):
                setattr(existing_task, key, value)

        session.add(existing_task)
    else:
        new_task = GeneratedTasksModel(
            user_id=user.id,
            **task_dict
        )
        session.add(new_task)

    await session.commit()

    return generated_data


@router.post('/generated_task_check', summary='Проверяет ответ на сгенерированную задачу')
async def check_sandbox_task(
        user_data: GeneratedTaskCheckRequest,
        session: SessionDep,
        user: UserDep
):

    query = select(GeneratedTasksModel).where(GeneratedTasksModel.user_id == user.id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сначала сгенерируйте задачу"
        )

    correct_ans = format_answer(task.correct_answer)
    user_ans = format_answer(user_data.answer)

    is_correct = user_ans == correct_ans

    return AnswerCheckResponse(
        is_correct=is_correct,
        message="Верно! 🎉" if is_correct else "Неверно! Попробуй еще раз."
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


