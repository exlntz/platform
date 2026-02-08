from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Model
from sqlalchemy import Text, ForeignKey, func, Enum as SQLEnum, Index, text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from app.core.constants import DifficultyLevel,Tag,Subject,RankName,Achievement


class UserModel(Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column(default=1000.0)
    user_rank: Mapped[RankName] = mapped_column(SQLEnum(RankName, native_enum=False),default=RankName.BRONZE,server_default="BRONZE")
    all_achievements: Mapped[list[Achievement]] = mapped_column(JSONB, default_factory=list)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    xp: Mapped[int] = mapped_column(default=0)
    avatar_url: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),init=False)


class TaskModel(Model):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
    subject: Mapped[Subject] = mapped_column(SQLEnum(Subject, native_enum=False), index=True)
    correct_answer: Mapped[str] = mapped_column()
    difficulty: Mapped[DifficultyLevel] = mapped_column(SQLEnum(DifficultyLevel, native_enum=False), index=True)
    tags: Mapped[list[Tag]] = mapped_column(JSONB, default_factory=list)
    hint: Mapped[str | None] = mapped_column(Text, default=None)

Index(
    'ix_tasks_fts',
    func.to_tsvector(text("'russian'"), TaskModel.title + ' ' + TaskModel.description),
    postgresql_using='gin'
)
Index('ix_tasks_tags', TaskModel.tags, postgresql_using='gin')

class AttemptModel(Model):
    __tablename__ = 'attempts'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    user_answer: Mapped[str] = mapped_column()
    is_correct: Mapped[bool] = mapped_column()
    time_spent: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),init=False)

Index(
    'ix_attempts_user_task_correct_created',
    AttemptModel.user_id,
    AttemptModel.task_id,
    AttemptModel.is_correct,
    AttemptModel.created_at
)

Index(
    'ix_attempts_user_created',
    AttemptModel.user_id,
    AttemptModel.created_at
)

class AuditLogModel(Model):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey('users.id'),index=True)
    action: Mapped[str] = mapped_column()
    target_id: Mapped[int | None] = mapped_column(default=None)
    details: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),init=False)


class PvPMatchModel(Model):
    __tablename__ = 'pvp_matches'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    player1_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    player2_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    p1_elo_change: Mapped[float] = mapped_column()
    p2_elo_change: Mapped[float] = mapped_column()
    result: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),insert_default=lambda: datetime.now(timezone.utc),init=False)


class EloHistoryModel(Model):
    __tablename__ = 'elo_history'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    rating: Mapped[float] = mapped_column() #рейтинг после матча
    change: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),insert_default=lambda: datetime.now(timezone.utc),init=False)


class GeneratedTasksModel(Model):
    __tablename__ = "generated_tasks"

    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
    subject: Mapped[Subject] = mapped_column(SQLEnum(Subject, native_enum=False), index=True)
    correct_answer: Mapped[str] = mapped_column()
    difficulty: Mapped[DifficultyLevel] = mapped_column(SQLEnum(DifficultyLevel, native_enum=False), index=True)
    tags: Mapped[list[Tag]] = mapped_column(JSONB, default_factory=list)
    hint: Mapped[str | None] = mapped_column(Text, default=None)