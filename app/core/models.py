from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Model
from sqlalchemy import Text, ForeignKey, func, Enum as SQLEnum, JSON
from datetime import datetime
from app.core.constants import DifficultyLevel,Tag,Subject,RankName,Achievement

class UserModel(Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    username: Mapped[str] = mapped_column(unique=True,index=True)
    email: Mapped[str] = mapped_column(unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column(default=1000.0)
    rank: Mapped[RankName] = mapped_column(
        SQLEnum(
            RankName,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x]
        ),
        default=RankName.BRONZE,
        server_default="Бронза"
    )
    achievements: Mapped[list[Achievement]] = mapped_column(JSON, default_factory=list)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    xp: Mapped[int] = mapped_column(default=0)
    avatar_url: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),init=False)


class TaskModel(Model):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
    subject: Mapped[Subject] = mapped_column(
        SQLEnum(
            Subject,
            native_enum=False,  # Храним как VARCHAR
            # Говорим SQLAlchemy использовать значения ("Физика") для проверки и записи
            values_callable=lambda obj: [e.value for e in obj]
        ),
        index=True
    )
    correct_answer: Mapped[str] = mapped_column()
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SQLEnum(
            DifficultyLevel,
            native_enum=False,
            # То же самое для сложности ("Easy" вместо "EASY")
            values_callable=lambda obj: [e.value for e in obj]
        ),
        index=True
    )
    tags: Mapped[list[Tag]] = mapped_column(JSON, default_factory=list)
    hint: Mapped[str | None] = mapped_column(Text, default=None)



class AttemptModel(Model):
    __tablename__ = 'attempts'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    user_answer: Mapped[str] = mapped_column()
    is_correct: Mapped[bool] = mapped_column()
    time_spent: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),init=False)


class AuditLogModel(Model):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey('users.id'),index=True)
    action: Mapped[str] = mapped_column()
    target_id: Mapped[int | None] = mapped_column(default=None)
    details: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),init=False)


class PvPMatchModel(Model):
    __tablename__ = 'pvp_matches'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    player1_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    player2_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    winner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    p1_elo_change: Mapped[float] = mapped_column()
    p2_elo_change: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, init=False)


class EloHistoryModel(Model):
    __tablename__ = 'elo_history'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    rating: Mapped[float] = mapped_column() #рейтинг после матча
    change: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, init=False)
