from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func, desc
from app.core.database import SessionDep
from app.models import UserModel, TaskModel, AttemptModel
from app.schemas.admin_schemas import UserAdminRead, AdminDashboardStats
from app.dependencies import AdminDep
from datetime import datetime, timedelta


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

@router.patch('/users/{user_id}/ban',summary='Заблокировать/Разблокировать пользователя (для админов)')
async def ban_user(
        user_id: int,
        session: SessionDep,
        admin: AdminDep
):
    user = await session.get(UserModel,user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Пользователь не найден')

    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Вы не можете заблокировать себя')

    user.is_banned = not user.is_banned

    await session.commit()

    status_text = 'заблокирован' if user.is_banned else 'разблокирован'

    return {'message': f'Пользователь {user.username} {status_text}'}


@router.patch('users/{user_id}/role',summary='Изменить роль пользователя (для админов)')
async def change_role(
        user_id: int,
        session: SessionDep,
        admin: AdminDep
):
    user = await session.get(UserModel,user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Пользователь не найден')


    user.is_admin = not user.is_admin
    await session.commit()

    role_text = 'назначен администратором' if user.is_admin else 'больше не администратор'

    return {'message':f'Пользователь {user.username} {role_text}'}

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