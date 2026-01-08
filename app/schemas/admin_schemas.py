from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.core.models import DifficultyLevel


class UserAdminRead(BaseModel):
    id: int
    username: str
    email: str
    rating: float
    is_admin: bool
    is_banned: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserAdminUpdate(BaseModel):
    username: str | None = Field(None,min_length=3,max_length=40)
    email: EmailStr | None = None
    rating: float | None = None
    is_admin: bool | None = None
    is_banned: bool | None = None


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
