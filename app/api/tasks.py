import json

from fastapi import APIRouter,HTTPException,status,Depends,Response,File,UploadFile
from typing import Annotated
from sqlalchemy import select
from app.database import SessionDep
from app.models import TaskModel, AttemptModel,UserModel
from app.schemas.task import TaskRead,TaskCreate, AnswerCheckRequest, AnswerCheckResponse
from app.dependencies import get_current_user
from app.models import DifficultyLevel
from json import dumps
from app.dependencies import AdminDep


router=APIRouter(prefix='/tasks',tags=['Задачи'])

@router.get('/')
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

@router.post('/')
async def create_task(
        new_task: TaskCreate,
        session: SessionDep,
        admin: AdminDep
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



@router.get('/export')
async def export_tasks(
        admin: AdminDep,
        session: SessionDep
):
    query=select(TaskModel)
    result = await session.execute(query)
    tasks = result.scalars().all()

    export_data = [
        {
            "title": t.title,
            "description": t.description,
            "subject": t.subject,
            "theme": t.theme,
            "difficulty": t.difficulty,
            "correct_answer": t.correct_answer
        } for t in tasks
    ]

    content = dumps(export_data,ensure_ascii=False,indent=4)

    return Response(
        content=content,
        media_type='application/json',
        headers={'Content-Disposition': 'attachment; filename="tasks_export.json"'}
    )




@router.post('/import')
async def import_tasks(
        session: SessionDep,
        admin: AdminDep,
        file: UploadFile = File(...)
):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Файл должен быть в формате JSON')

    try:
        content = await file.read()
        tasks = json.loads(content)

        if not isinstance(tasks,list):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Ожидался список задач')

        count_new_tasks = 0
        for item in tasks:
            task = TaskModel(
                title=item.get("title"),
                description=item.get("description"),
                subject=item.get("subject"),
                theme=item.get("theme"),
                difficulty=item.get("difficulty"),
                correct_answer=item.get("correct_answer")
            )
            session.add(task)
            count_new_tasks+=1

        await session.commit()

        return {'message': f'Успешно импортировано задач: {count_new_tasks}'}

    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка в структуре JSON-файла")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Произошла ошибка при импорте: {str(e)}")



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

    if task is None:
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


@router.get('/{task_id}')
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