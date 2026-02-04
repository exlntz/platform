from pydantic import BaseModel, Field, model_validator
from app.core.constants import DifficultyLevel,Tag,Subject,SUBJECT_TO_TAGS, Achievement

class TaskBase(BaseModel):
    title: str
    description: str
    subject: Subject
    tags: list[Tag] = Field(default_factory=list)
    difficulty: DifficultyLevel
    hint: str | None = None

    @model_validator(mode='after')
    def validate_tags(self):
        if self.subject in SUBJECT_TO_TAGS:
            allowed_tags = SUBJECT_TO_TAGS[self.subject]
            for t in self.tags:
                if t not in allowed_tags:
                    raise ValueError(f"Тег '{t}' не разрешен для предмета '{self.subject}'")
        return self


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
    time_spent: int

class AnswerCheckResponse(BaseModel):
    is_correct: bool
    correct_answer: str | None = None
    message: str
    achievements: list[str]

class TaskAdminRead(TaskRead):
    correct_answer: str
