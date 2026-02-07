from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

from app.core.constants import Achievement
from app.core.models import DifficultyLevel
from app.schemas.user import UserProfileRead, UserStatsResponse


class UserAdminRead(BaseModel):
    id: int
    username: str
    email: str
    rating: float
    is_admin: bool
    is_banned: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAdminUpdate(BaseModel):
    username: str | None = Field(None,min_length=3,max_length=40)
    email: EmailStr | None = None
    rating: float | None = None
    is_admin: bool | None = None
    is_banned: bool | None = None
    avatar_url: str | None = None
    achievements: list[Achievement] | None
    xp: int | None = None


class TaskAdminUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    subject: str | None = None
    theme: str | None = None
    difficulty: DifficultyLevel | None = None
    correct_answer: str | None = None


class AdminDashboardStats(BaseModel):
    total_users: int
    total_tasks: int
    average_rating: float
    new_users_24h: int
    most_popular_subject: str


class EloPoint(BaseModel):
    rating: float
    change: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserEloHistoryResponse(BaseModel):
    username: str
    current_rating: float
    history: list[EloPoint]


class AuditLogRead(BaseModel):
    id: int
    admin_username: str
    action: str
    target_id: int | None = None
    details: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserFullResponse(BaseModel):
    profile: UserProfileRead
    stats: UserStatsResponse
    elo_history: list[EloPoint]