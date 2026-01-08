from fastapi import APIRouter, HTTPException, status, Response, File, UploadFile
from pydantic import model_validator
from sqlalchemy import select, func, desc
from app.core.database import SessionDep
from app.core.models import UserModel, TaskModel, AttemptModel
from app.schemas.admin_schemas import UserAdminRead, AdminDashboardStats, UserAdminUpdate, TaskAdminUpdate
from datetime import datetime, timedelta
from app.schemas.task import TaskAdminRead, TaskRead, TaskCreate
import json
from app.core.dependencies import AdminDep


router = APIRouter(prefix='/admin',tags=['Админ панель'])


@router.get('/users',summary='Список всех пользователей (для админов)')
async def get_all_users(
        session: SessionDep,
        admin: AdminDep,
        limit: int = 100,
        offset: int = 0
) -> list[UserAdminRead]:
    query = (
        select(UserModel)
        .order_by(UserModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result= await session.execute(query)
    users = list(result.scalars().all())
    return users

@router.patch('/users/{user_id}',summary='Изменить информацию о пользователе (для админов)')
async def update_user(
        user_id: int,
        update_data: UserAdminUpdate,
        session: SessionDep,
        admin: AdminDep,
):
    user = await session.get(UserModel,user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Пользователь не найден')

    if update_data.username and update_data.username != user.username:
        exists = await session.execute(select(UserModel).where(UserModel.username == update_data.username))
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Это имя пользователя уже занято")

    if update_data.email and update_data.email != user.email:
        exists = await session.execute(select(UserModel).where(UserModel.email == update_data.email))
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот Email уже используется другим аккаунтом")

    if user.id == admin.id and (update_data.is_admin == False or update_data.is_banned == True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Вы не можете лишить прав или забанить самого себя')

    data  = update_data.model_dump(exclude_unset=True)

    for key,value in data.items():
        setattr(user,key,value)

    await session.commit()
    return {'message': f'Данные пользователя {user.username} успешно обновлены'}

@router.delete('/users/{user_id}',summary='Удалить пользователя (для админов)')
async def delete_user(
        user_id: int,
        session: SessionDep,
        admin: AdminDep
):
    user = await session.get(UserModel,user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Пользователь не найден')

    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Вы не можете удалить самого себя')

    await session.delete(user)
    await session.commit()

    return {'message': f'Пользователь {user.username} успешно удален'}

@router.get('/stats',summary='Статистика для дашборда (для админов)')
async def get_admin_stats(
        session: SessionDep,
        admin: AdminDep
) -> AdminDashboardStats:
    good_time = datetime.now() - timedelta(hours=24)

    total_users = await session.scalar(select(func.count(UserModel.id))) or 0
    total_tasks = await session.scalar(select(func.count(TaskModel.id))) or 0

    avg_rating = await session.scalar(select(func.avg(UserModel.rating))) or 0

    new_users = await session.scalar(select(func.count(UserModel.id)).where(UserModel.created_at >= good_time)) or 0

    popular_subject_query = (
        select(TaskModel.subject)
        .join(AttemptModel, AttemptModel.task_id == TaskModel.id)
        .group_by(TaskModel.subject)
        .order_by(desc(func.count(TaskModel.id)))
        .limit(1)
    )

    result = await session.execute(popular_subject_query)

    popular_subject = result.scalar() or 'Нет данных'

    return AdminDashboardStats(
        total_users=total_users,
        total_tasks=total_tasks,
        average_rating=round(float(avg_rating), 1),
        new_users_24h=new_users,
        most_popular_subject=popular_subject
    )


@router.post('/tasks/create',summary='Создать задачу (для админов)')
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
        difficulty=new_task.difficulty.capitalize(),
        correct_answer=new_task.correct_answer)

    session.add(task_db)
    await session.commit()
    await session.refresh(task_db)

    return TaskRead.model_validate(task_db)



@router.get('/tasks/export',summary='Экспорт задач (для админов)',description='Получение JSON файла со всеми задачами')
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

    content = json.dumps(export_data,ensure_ascii=False,indent=4)

    return Response(
        content=content,
        media_type='application/json',
        headers={'Content-Disposition': 'attachment; filename="tasks_export.json"'}
    )


@router.post('/tasks/import',summary='Импорт задач (для админов)',description='Импорт задач. Если задача с таким названием существует, то обновляем ее, если нет, то создаем новую')
async def import_tasks(
        session: SessionDep,
        admin: AdminDep,
        file: UploadFile = File(...)
):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Файл должен быть в формате JSON')

    try:
        content = await file.read()
        data = json.loads(content)

        if not isinstance(data,list):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Ожидался список задач')


        incoming_titles = [item.get("title") for item in data if item.get("title")]

        query = select(TaskModel).where(TaskModel.title.in_(incoming_titles))
        result = await session.execute(query)
        existing_tasks = {t.title: t for t in result.scalars().all()}

        created_count = 0
        updated_count = 0


        for item in data:
            title = item.get('title')
            if not title:
                continue

            raw_difficulty = item.get('difficulty')
            clean_difficulty = raw_difficulty.capitalize() if raw_difficulty else None

            if title in existing_tasks:
                task = existing_tasks[title]
                task.description = item.get("description", task.description)
                task.subject = item.get("subject", task.subject)
                task.theme = item.get("theme", task.theme)

                if raw_difficulty:
                    task.difficulty = clean_difficulty

                task.correct_answer = item.get("correct_answer", task.correct_answer)
                updated_count += 1
            else:
                new_task = TaskModel(
                    title=title,
                    description=item.get("description"),
                    subject=item.get("subject"),
                    theme=item.get("theme"),
                    difficulty=clean_difficulty,
                    correct_answer=item.get("correct_answer")
                )
                session.add(new_task)
                created_count += 1

        await session.commit()

        return {
            "message": "Импорт завершен успешно",
            "created": created_count,
            "updated": updated_count
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка в структуре JSON-файла")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Произошла ошибка при импорте: {str(e)}")





@router.get('/tasks/{task_id}', summary='Получить полную задачу с ответом (для админов)')
async def get_admin_task_details(
        task_id: int,
        session: SessionDep,
        admin: AdminDep
) -> TaskAdminRead:
    task = await session.get(TaskModel, task_id)

    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')

    return TaskAdminRead.model_validate(task)


@router.delete('/tasks/{task_id}', summary='Удалить задачу (для админов)')
async def delete_task(
        task_id: int,
        session: SessionDep,
        admin: AdminDep
):
    task = await session.get(TaskModel, task_id)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Задача не найдена')

    await session.delete(task)
    await session.commit()

    return {'message': f'Задача #{task_id} успешно удалена'}


@router.patch('/tasks/{task_id}', summary='Редактировать задачу (для админов)')
async def update_task(
        task_id: int,
        update_data: TaskAdminUpdate,
        session: SessionDep,
        admin: AdminDep
) -> TaskRead:

    task = await session.get(TaskModel, task_id)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    data = update_data.model_dump(exclude_unset=True)

    for key,value in data.items():

        if key == 'difficulty' and value:
            value = value.capitalize()

        setattr(task,key,value)

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)

