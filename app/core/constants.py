# app/core/constants.py
from enum import Enum

class BaseStrEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None

class Subject(BaseStrEnum):
    PYTHON = "Python"
    MATH = 'Математика'
    INF = 'Информатика'
    RUSS = 'Русский язык'
    ENGLISH = 'Английский язык'
    PHYS = 'Физика'

class Tag(BaseStrEnum):
    ARITHMETIC = "Арифметика"
    GEOM = 'Геометрия'
    ALGEBRA = 'Алгебра'
    TRIG = 'Тригонометрия'

    TYPES = 'Типы данных'

    SYS = 'Системы счисления'

    SENTENCES = 'Виды предложений'

    TIMES = 'Времена'

    SECTIONS = 'Разделы физики'

class DifficultyLevel(BaseStrEnum):
    EASY = 'Easy'
    MEDIUM = 'Medium'
    HARD = 'Hard'

class RankName(BaseStrEnum):
    BRONZE = "Бронза"
    SILVER = "Серебро"
    GOLD = "Золото"
    ELITE = "Элита"
    SENSEI = "Сенсей"
    LEGEND = "Легенда"

class Achievement(BaseStrEnum):
    FIRST_WIN = "First win"
    FIRST_STEP = "First step"
    PROFILE_MASTER = "Profile master"
    TASK_MASTER = "Task master"
    KNOWLEDGE_TITAN = "Knowledge titan"
    CENTURION = "Centurion"
    SPEEDRUNNER = "Speedrunner"
    INTELLECTUAL = "Intellectual"
    INVINCIBLE = "Invincible"
    PROGRAMMING_GURU = "Programming guru"
    MATH_WIZARD = "Math wizard"
    LOGIC_KING = "Logic king"
    EARLY_BIRD = "Early bird"
    STREAK_7 = "Streak 7"


SUBJECT_TO_TAGS = {
    Subject.PYTHON: [Tag.TYPES],
    Subject.MATH: [Tag.ALGEBRA,Tag.ARITHMETIC,Tag.TRIG,Tag.GEOM],
    Subject.INF: [Tag.SYS],
    Subject.RUSS: [Tag.SENTENCES],
    Subject.ENGLISH: [Tag.TIMES],
    Subject.PHYS: [Tag.SECTIONS],

}