from sqlalchemy.orm import Mapped,mapped_column
from app.database import Model
from sqlalchemy import Text, ForeignKey, func
from datetime import datetime


class UserModel(Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    username: Mapped[str] = mapped_column(unique=True,index=True)
    email: Mapped[str] = mapped_column(unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column(default=1000.0)
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: datetime = mapped_column(server_default=func.now(),init=False)


class TaskModel(Model):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(index=True)
    theme: Mapped[str] = mapped_column(index=True)
    difficulty: Mapped[str] = mapped_column(index=True)
    correct_answer: Mapped[str] = mapped_column()


class AttemptModel(Model):
    __tablename__ = 'attempts'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    user_answer: Mapped[str] = mapped_column()
    is_correct: Mapped[bool] = mapped_column()
    time: Mapped[datetime] = mapped_column(server_default=func.now(),init=False)
