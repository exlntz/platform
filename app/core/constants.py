from enum import Enum


class BaseStrEnum(str, Enum):
    @property
    def label(self):
        return SUBJECT_DISPLAY.get(self) or TAG_DISPLAY.get(self) or self.value

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v_upper = value.upper()
            for member in cls:
                if member.value == v_upper:
                    return member
        return None


class Subject(BaseStrEnum):
    PYTHON = "PYTHON"
    MATH = "MATH"
    INF = "INF"
    RUSS = "RUSS"
    ENGLISH = "ENGLISH"
    PHYS = "PHYS"
    ASTROPHYSICS = "ASTROPHYSICS"


class Tag(BaseStrEnum):
    SPACE = "SPACE"
    LOGARITHMS = "LOGARITHMS"
    ARITHMETIC = "ARITHMETIC"

    GEOM = "GEOM"
    ALGEBRA = "ALGEBRA"
    TRIG = "TRIG"
    TYPES = "TYPES"
    SYS = "SYS"
    SENTENCES = "SENTENCES"
    TIMES = "TIMES"
    SECTIONS = "SECTIONS"


class DifficultyLevel(BaseStrEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class RankName(BaseStrEnum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    ELITE = "ELITE"
    SENSEI = "SENSEI"
    LEGEND = "LEGEND"

class Achievement(BaseStrEnum):
    FIRST_STEP = "FIRST_STEP"  # Решил 1 задачу
    GURU = "GURU"  # Решил 10 задач
    PROFILE_MASTER = "PROFILE_MASTER" # Поставил аватарку

    @property
    def label(self):
        labels = {
            Achievement.FIRST_STEP: "Первый шаг",
            Achievement.GURU: "Гуру",
            Achievement.PROFILE_MASTER: "Красавчик!"
        }
        return labels.get(self, self.value)



SUBJECT_DISPLAY = {
    Subject.PYTHON: "Python",
    Subject.MATH: "Математика",
    Subject.INF: "Информатика",
    Subject.RUSS: "Русский язык",
    Subject.ENGLISH: "Английский язык",
    Subject.PHYS: "Физика",
    Subject.ASTROPHYSICS: "Астрофизика"
}

TAG_DISPLAY = {
    Tag.SPACE: "Космос",
    Tag.LOGARITHMS: "Логарифмы",
    Tag.ARITHMETIC: "Арифметика",
    Tag.GEOM: "Геометрия",
    Tag.ALGEBRA: "Алгебра",
    Tag.TRIG: "Тригонометрия",
    Tag.TYPES: "Типы данных",
    Tag.SYS: "Системы счисления",
    Tag.SENTENCES: "Виды предложений",
    Tag.TIMES: "Времена",
    Tag.SECTIONS: "Разделы физики"
}

SUBJECT_TO_TAGS = {
    Subject.PYTHON: [Tag.TYPES],
    Subject.MATH: [Tag.ALGEBRA, Tag.ARITHMETIC, Tag.TRIG, Tag.GEOM, Tag.LOGARITHMS],
    Subject.INF: [Tag.SYS],
    Subject.RUSS: [Tag.SENTENCES],
    Subject.ENGLISH: [Tag.TIMES],
    Subject.PHYS: [Tag.SECTIONS],
    Subject.ASTROPHYSICS: [Tag.SPACE, Tag.LOGARITHMS]
}