from enum import Enum


class BaseStrEnum(str, Enum):
    @property
    def label(self) -> str:
        return self.value

    @classmethod
    def to_list(cls):
        return [
            {
                "key": item.value,
                "label": item.label,
            }
            for item in cls
        ]


class Subject(BaseStrEnum):
    ENGLISH = "ENGLISH"
    PYTHON = "PYTHON"
    MATH = "MATH"
    INF = "INF"
    RUSS = "RUSS"
    PHYS = "PHYS"


    @property
    def label(self):
        labels = {
            Subject.PYTHON: "Python",
            Subject.MATH: "Математика",
            Subject.INF: "Информатика",
            Subject.RUSS: "Русский язык",
            Subject.PHYS: "Физика",
            Subject.ENGLISH: "Англ. язык"
        }
        return labels[self]


class Tag(BaseStrEnum):
    TYPES = "TYPES"
    OOP = "OOP"
    WEB = "WEB"
    LOGARITHMS = "LOGARITHMS"
    ARITHMETIC = "ARITHMETIC"
    GEOM = "GEOM"
    ALGEBRA = "ALGEBRA"
    TRIG = "TRIG"
    SYS = "SYS"
    DP = "DP"
    GRAPHS = "GRAPHS"
    SENTENCES = "SENTENCES"
    ORTHOGRAPHY = "ORTHOGRAPHY"
    PUNCTUATION = "PUNCTUATION"
    TIMES = "TIMES"
    GRAMMAR = "GRAMMAR"
    VOCABULARY = "VOCABULARY"
    SECTIONS = "SECTIONS"
    MECHANICS = "MECHANICS"
    THERMO = "THERMO"

    @property
    def label(self) -> str:
        labels = {
            Tag.TYPES: "Типы данных",
            Tag.OOP: "ООП",
            Tag.WEB: "Веб-разработка",
            Tag.LOGARITHMS: "Логарифмы",
            Tag.ARITHMETIC: "Арифметика",
            Tag.GEOM: "Геометрия",
            Tag.ALGEBRA: "Алгебра",
            Tag.TRIG: "Тригонометрия",
            Tag.SYS: "Системы счисления",
            Tag.DP: "Динамическое программирование",
            Tag.GRAPHS: "Теория графов",
            Tag.SENTENCES: "Синтаксис и предложения",
            Tag.ORTHOGRAPHY: "Орфография",
            Tag.PUNCTUATION: "Пунктуация",
            Tag.TIMES: "Времена (Tenses)",
            Tag.GRAMMAR: "Грамматика",
            Tag.VOCABULARY: "Лексика",
            Tag.SECTIONS: "Разделы физики",
            Tag.MECHANICS: "Механика",
            Tag.THERMO: "Термодинамика",
        }
        return labels[self]


class DifficultyLevel(BaseStrEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

    @property
    def label(self):
        labels = {
            self.EASY: "Легкая",
            self.MEDIUM: "Средняя",
            self.HARD: "Сложная"
        }
        return labels[self]


class RankName(BaseStrEnum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    ELITE = "ELITE"
    SENSEI = "SENSEI"
    LEGEND = "LEGEND"

    @property
    def label(self):
        labels = {
            RankName.BRONZE: "Бронза",
            RankName.SILVER: "Серебро",
            RankName.GOLD: "Золото",
            RankName.ELITE: "Элита",
            RankName.SENSEI: "Сенсей",
            RankName.LEGEND: "Легенда"
        }
        return labels[self]

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
        return labels[self]

SUBJECT_TO_TAGS = {
    Subject.PYTHON: [
        Tag.TYPES, Tag.OOP, Tag.WEB
    ],
    Subject.MATH: [
        Tag.LOGARITHMS, Tag.ARITHMETIC, Tag.GEOM, Tag.ALGEBRA, Tag.TRIG
    ],
    Subject.INF: [
        Tag.SYS, Tag.DP, Tag.GRAPHS
    ],
    Subject.RUSS: [
        Tag.SENTENCES, Tag.ORTHOGRAPHY, Tag.PUNCTUATION
    ],
    Subject.ENGLISH: [
        Tag.TIMES, Tag.GRAMMAR, Tag.VOCABULARY
    ],
    Subject.PHYS: [
        Tag.SECTIONS, Tag.MECHANICS, Tag.THERMO
    ],
}