from pydantic import BaseModel
from app.models import DifficultyLevel

class TaskBase(BaseModel):
    title: str
    description: str
    subject: str
    theme: str
    difficulty: DifficultyLevel

class TaskRead(TaskBase): # 1. Наследуем (оставляем старые поля)
    id: int               # 2. Приписываем новое поле (id)

    # 3. Настраиваем "мостик" с базой данных
    model_config = {
        "from_attributes": True
    }

class TaskCreate(TaskBase):
    correct_answer: str

class AnswerCheckRequest(BaseModel):
    answer: str

class AnswerCheckResponse(BaseModel):
    is_correct: bool
    correct_answer: str | None = None
    message: str