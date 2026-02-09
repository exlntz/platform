from fastapi import APIRouter, HTTPException, status, Response, File, UploadFile, Query
from sqlalchemy import select, func, desc, distinct
from sqlalchemy.orm import aliased
from app.core.constants import SUBJECT_TO_TAGS
from app.core.database import SessionDep
from app.core.models import UserModel, TaskModel, AttemptModel, AuditLogModel, PvPMatchModel
from app.schemas.admin_schemas import UserAdminRead, AdminDashboardStats, UserAdminUpdate, TaskAdminUpdate, \
    AuditLogRead, AdminUserFullResponse, AdminPvpMatchesHistoryPlayer, BanUserRequest, PromoteUserRequest
from datetime import datetime, timedelta, timezone
from app.schemas.task import TaskAdminRead, TaskRead, TaskCreate
import json
import csv
import io
from app.core.dependencies import AdminDep
from app.utils.changes import calculate_changes
from app.services.user_stats import calculate_user_stats,calculate_profile_info,calculate_elo_history

router = APIRouter(prefix='/admin', tags=['Админ панель'])


async def log_admin_action(
        session,
        admin_id: int,
        action: str,
        target_id: int = None,
        details: str = None
):
    new_log = AuditLogModel(
        admin_id=admin_id,
        action=action,
        target_id=target_id,
        details=details,
    )
    session.add(new_log)


@router.get('/users', summary='Список всех пользователей (для админов)')
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
    result = await session.execute(query)
    users = list(result.scalars().all())
    return users


@router.patch('/users/{user_id}', summary='Изменить информацию о пользователе (для админов)')
async def update_user(
        user_id: int,
        update_data: UserAdminUpdate,
        session: SessionDep,
        admin: AdminDep,
):
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')

    if update_data.username and update_data.username != user.username:
        exists = await session.execute(select(UserModel).where(UserModel.username == update_data.username))
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Это имя пользователя уже занято")

    if update_data.email and update_data.email != user.email:
        exists = await session.execute(select(UserModel).where(UserModel.email == update_data.email))
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Этот Email уже используется другим аккаунтом")


    data = update_data.model_dump(exclude_unset=True)

    changes_log = calculate_changes(user, data)

    for key, value in data.items():
        setattr(user, key, value)

    if changes_log:
        await log_admin_action(
            session=session,
            admin_id=admin.id,
            action="update_user",
            target_id=user.id,
            details=changes_log
        )

    await session.commit()
    return {'message': f'Данные пользователя {user.username} успешно обновлены'}


@router.patch("/users/{user_id}/ban", summary="Заблокировать/Разблокировать пользователя (для админов)")
async def set_user_ban_status(
        user_id: int,
        data: BanUserRequest,
        session: SessionDep,
        admin: AdminDep,
):

    user = await session.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете заблокировать самого себя"
        )

    previous_status = user.is_banned
    user.is_banned = data.is_banned

    action_text = "заблокирован" if data.is_banned else "разблокирован"

    await log_admin_action(
        session=session,
        admin_id=admin.id,
        action=f"Пользователь {action_text}",
        target_id=user.id,
        details=f"Статус изменен с {previous_status} на {user.is_banned}"
    )

    await session.commit()

    msg = "Пользователь заблокирован" if data.is_banned else "Пользователь разблокирован"
    return {"message": msg, "user_id": user.id, "is_banned": user.is_banned}



@router.patch("/users/{user_id}/promote", summary="Выдать/Снять права администратора (для админов)")
async def set_user_admin_status(
        user_id: int,
        data: PromoteUserRequest,
        session: SessionDep,
        admin: AdminDep,
):

    user = await session.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    if user.id == admin.id and data.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете лишить прав администратора самого себя"
        )

    user.is_admin = data.is_admin

    action_text = "теперь админ" if data.is_admin else "больше не админ"

    await log_admin_action(
        session=session,
        admin_id=admin.id,
        action=action_text,
        target_id=user.id,
        details=f"Статус админа был изменен на {user.is_admin}"
    )

    await session.commit()

    msg = "Права администратора выданы" if data.is_admin else "Права администратора отозваны"
    return {"message": msg, "user_id": user.id, "is_admin": user.is_admin}


@router.delete('/users/{user_id}', summary='Удалить пользователя (для админов)')
async def delete_user(
        user_id: int,
        session: SessionDep,
        admin: AdminDep
):
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')

    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы не можете удалить самого себя')

    await log_admin_action(
        session=session,
        admin_id=admin.id,
        action="delete_user",
        target_id=user_id,
        details=f"Deleted user: {user.username} (Email: {user.email})"
    )

    await session.delete(user)
    await session.commit()

    return {'message': f'Пользователь {user.username} успешно удален'}

@router.get('/users/{user_id}/full_details',summary='Возвращает полную информацию о пользователе (для админов)',response_model=AdminUserFullResponse)
async def get_user_full_details(
        user_id: int,
        session: SessionDep,
        admin: AdminDep
) -> AdminUserFullResponse:

    user = await session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Пользователь не найден')

    profile_info = await calculate_profile_info(session,user_id)
    subject_stats = await calculate_user_stats(session,user_id)
    elo_history = await calculate_elo_history(session,user_id)

    return AdminUserFullResponse(
        profile=profile_info,
        stats=subject_stats,
        elo_history=elo_history
    )

@router.get('/stats', summary='Статистика для дашборда (для админов)')
async def get_admin_stats(
        session: SessionDep,
        admin: AdminDep
) -> AdminDashboardStats:
    good_time = datetime.now(timezone.utc) - timedelta(hours=24)

    total_users = await session.scalar(select(func.count(UserModel.id))) or 0
    total_tasks = await session.scalar(select(func.count(TaskModel.id))) or 0
    new_users = await session.scalar(select(func.count(UserModel.id)).where(UserModel.created_at >= good_time)) or 0
    total_pvp_matches = await session.scalar(select(func.count(PvPMatchModel.id))) or 0
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
        new_users_24h=new_users,
        most_popular_subject=popular_subject,
        total_pvp_matches=total_pvp_matches
    )


@router.post('/tasks/create', summary='Создать задачу (для админов)',response_model=TaskRead)
async def create_task(
        new_task: TaskCreate,
        session: SessionDep,
        admin: AdminDep
) -> TaskRead:
    task_db = TaskModel(**new_task.model_dump())

    session.add(task_db)

    await session.flush()

    await log_admin_action(
        session=session,
        admin_id=admin.id,
        action="create_task",
        target_id=task_db.id,
        details=f"Task created: '{task_db.title}' (Subject: {task_db.subject})"
    )

    await session.commit()
    await session.refresh(task_db)

    return TaskRead.model_validate(task_db)


@router.get('/tasks/export', summary='Экспорт задач JSON/CSV (для админов)')
async def export_tasks(
        session: SessionDep,
        admin: AdminDep,
        export_format: str = Query("json", enum=["json", "csv"], alias="format")
):

    tasks = (await session.execute(select(TaskModel))).scalars().all()

    data = [TaskAdminRead.model_validate(t).model_dump() for t in tasks]

    if export_format == "json":
        return Response(
            content=json.dumps(data, ensure_ascii=False, indent=4),
            media_type='application/json',
            headers={'Content-Disposition': 'attachment; filename="tasks.json"'}
        )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()

    for row in data:
        row['tags'] = ", ".join(row['tags']) if isinstance(row['tags'], list) else ""
        writer.writerow(row)

    content = output.getvalue().encode('utf-8-sig')

    return Response(
        content=content,
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="tasks_export.csv"'}
    )


@router.post('/tasks/import', summary='Импорт задач JSON/CSV (для админов)',
             description='Поддерживает форматы .json и .csv. Обновляет существующие задачи по названию или создает новые.')
async def import_tasks(
        session: SessionDep,
        admin: AdminDep,
        file: UploadFile = File(...)
):
    content = await file.read()
    data = []

    try:
        if file.filename.endswith('.json'):
            data = json.loads(content)
        elif file.filename.endswith('.csv'):
            decoded_content = content.decode('utf-8')
            f = io.StringIO(decoded_content)
            reader = csv.DictReader(f)
            for row in reader:
                if 'tags' in row and row['tags']:
                    row['tags'] = [t.strip() for t in row['tags'].split(',')]
                else:
                    row['tags'] = []
                data.append(row)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Поддерживаются только .json и .csv файлы")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка при чтении файла: {str(e)}")

    if not isinstance(data, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверная структура данных: ожидался список задач')

    incoming_titles = [item.get("title") for item in data if item.get("title")]
    query = select(TaskModel).where(TaskModel.title.in_(incoming_titles))
    result = await session.execute(query)
    existing_tasks = {t.title: t for t in result.scalars().all()}

    created_count = 0
    updated_count = 0

    for item in data:
        title = item.get('title')
        if not title: continue

        if title in existing_tasks:
            task = existing_tasks[title]
            task.description = item.get("description", task.description)
            task.subject = item.get("subject", task.subject)
            task.tags = item.get("tags", task.tags)
            task.hint = item.get("hint", task.hint)
            task.difficulty = item.get("difficulty", task.difficulty)
            task.correct_answer = item.get("correct_answer", task.correct_answer)
            updated_count += 1
        else:
            new_task = TaskModel(
                title=title,
                description=item.get("description", ""),
                subject=item.get("subject", "Общее"),
                tags=item.get("tags", []),
                hint=item.get("hint"),
                difficulty=item.get("difficulty", "Easy"),
                correct_answer=item.get("correct_answer", "")
            )
            session.add(new_task)
            created_count += 1

    await log_admin_action(
        session=session,
        admin_id=admin.id,
        action="import_tasks",
        details=f"File: {file.filename}. Created: {created_count}, Updated: {updated_count}"
    )
    await session.commit()

    return {"message": "Импорт завершен", "created": created_count, "updated": updated_count}


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')

    await log_admin_action(
        session=session,
        admin_id=admin.id,
        action="delete_task",
        target_id=task_id,
        details=f"Deleted task: '{task.title}' (Subject: {task.subject})"
    )

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

    target_subject = data.get('subject', task.subject)
    target_tags = data.get('tags', task.tags)
    if target_subject and target_tags:
        allowed_tags = SUBJECT_TO_TAGS.get(target_subject, [])
        for tag in target_tags:
            if tag not in allowed_tags:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Тег '{tag}' нельзя добавить к предмету '{target_subject}'"
                )

    changes_log = calculate_changes(task, data)

    for key, value in data.items():
        setattr(task, key, value)

    if changes_log:
        await log_admin_action(
            session=session,
            admin_id=admin.id,
            action="update_task",
            target_id=task.id,
            details=changes_log
        )

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


@router.get('/stats/most_popular_subject', summary='Самый популярный предмет (для админов)')
async def get_most_popular_subject(
        session: SessionDep,
        admin: AdminDep,
):
    query = (
        select(TaskModel.subject)
        .join(AttemptModel, AttemptModel.task_id == TaskModel.id)
        .group_by(TaskModel.subject)
        .order_by(desc(func.count(distinct(AttemptModel.user_id))))
        .limit(1)
    )

    result = await session.execute(query)
    most_popular_subject = result.scalar_one_or_none()

    return {'most_popular_subject': most_popular_subject if most_popular_subject else 'Нет данных'}


@router.get('/logs',summary='Логи действий админов (для админов)',response_model=list[AuditLogRead])
async def get_logs(
        session: SessionDep,
        admin: AdminDep,
        limit: int = 20,
        offset: int = 0
):
    query = (
        select(
            AuditLogModel.id,
            AuditLogModel.admin_id,  # если нужно в схеме
            UserModel.username.label("admin_username"),
            AuditLogModel.action,
            AuditLogModel.target_id,
            AuditLogModel.details,
            AuditLogModel.created_at
        )
        .join(UserModel, AuditLogModel.admin_id == UserModel.id)
        .order_by(AuditLogModel.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(query)

    return result.mappings().all()



@router.get('/pvp_matches_history', summary='История матчей всех пользователей (для админов)')
async def get_pvp_matches_history(
        session: SessionDep,
        admin: AdminDep,
        limit: int = 20,
        offset: int = 0
) -> list[AdminPvpMatchesHistoryPlayer]:

    Player1 = aliased(UserModel)
    Player2 = aliased(UserModel)

    query = (
        select(
            PvPMatchModel.id,
            Player1.username.label("player1_username"),
            Player2.username.label("player2_username"),
            PvPMatchModel.p1_elo_change,
            PvPMatchModel.p2_elo_change,
            PvPMatchModel.result,
            PvPMatchModel.created_at
        )
        .join(Player1, PvPMatchModel.player1_id == Player1.id)
        .join(Player2, PvPMatchModel.player2_id == Player2.id)
        .order_by(PvPMatchModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await session.execute(query)
    return result.mappings().all()
