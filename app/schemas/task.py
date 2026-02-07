from pydantic import BaseModel, Field, model_validator, ConfigDict
from app.core.constants import DifficultyLevel, Tag, Subject, SUBJECT_TO_TAGS, Achievement


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


class TaskRead(TaskBase):
    id: int
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
class TaskCreate(TaskBase):
    correct_answer: str

class AnswerCheckRequest(BaseModel):
    answer: str
    time_spent: int

class AnswerCheckResponse(BaseModel):
    is_correct: bool
    correct_answer: str | None = None
    message: str
    achievements: list[Achievement]

class TaskAdminRead(TaskRead):
    correct_answer: str

class GeneratedTask(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(description="Привлекательный заголовок задачи")
    description: str = Field(description="Условие задачи с использованием LaTeX для формул")
    correct_answer: str = Field(description="Четкий краткий ответ (число или слово)")
    subject: Subject = Field(description='Предмет')
    difficulty: DifficultyLevel = Field(description='Уровень сложности')
    tags: list[Tag] = Field(description="Список тегов из предоставленного перечня")
    hint: str = Field(description="Подсказка, направляющая ход мыслей")

