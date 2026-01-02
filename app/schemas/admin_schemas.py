from pydantic import BaseModel
from datetime import datetime


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

class AdminDashboardStats(BaseModel):
    total_users: int
    total_tasks: int
    average_rating: float
    new_users_24h: int
    most_popular_subject: str
