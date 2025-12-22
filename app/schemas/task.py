from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str
    subject: str
    theme: str
    difficulty: str

class TaskRead(TaskBase): # 1. Наследуем (оставляем старые поля)
    id: int               # 2. Приписываем новое поле (id)

    # 3. Настраиваем "мостик" с базой данных
    model_config = {
        "from_attributes": True
    }

class TaskCreate(TaskBase):
    correct_answer: str