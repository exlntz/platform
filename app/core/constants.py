from enum import Enum

class BaseStrEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
        return None


class Subject(BaseStrEnum):
    MATH = "Математика"
    PHYSICS = "Физика"
    CHEMISTRY = "Химия"
    INFORMATICS = "Информатика"

    PYTHON = "Python"
    WEB_DEV = "Web-разработка"
    DATABASES = "Базы данных"
    ALGORITHMS = "Алгоритмы"

    LOGIC = "Логика"
    ENGLISH = "Английский язык"

class Tag(BaseStrEnum):
    ALGEBRA = "Алгебра"
    GEOMETRY = "Геометрия"
    PROBABILITY = "Теория вероятностей"
    TRIGONOMETRY = "Тригонометрия"

    ASYNC = "Асинхронность"
    DECORATORS = "Декораторы"
    OOP = "ООП"
    DATA_TYPES = "Типы данных"

    HTML_CSS = "HTML/CSS"
    REACT = "React"
    FASTAPI = "FastAPI"
    SQL_BASICS = "Основы SQL"

    SEQUENCES = "Последовательности"
    SORTING = "Сортировки"
    GRAPHS = "Графы"
    RECURSION = "Рекурсия"

    ELECTRICITY = "электричество"
    LAWS = "законы"
    SPACE = "космос"
    LIGHT = "свет"
    DYNAMICS = "динамика"
    FORCES = "силы"
    MECHANICS = "механика"
    ENERGY = "энергия"

    AREA = "площадь"
    STEREOMETRY = "стереометрия"
    VOLUME = "объем"
    COMBINATORICS = "комбинаторика"
    NUMBERS = "числа"
    EQUATIONS = "уравнения"
    LOGARITHMS = "логарифмы"
    ARITHMETIC = "арифметика"

    SEARCH = "поиск"
    DATA_STRUCTURES = "структуры данных"
    MEMORY = "память"
    TERMINOLOGY = "терминология"
    NUMBER_SYSTEMS = "системы счисления"
    BASICS = "основы"
    BOOLEAN_ALGEBRA = "булева алгебра"
    DB_SHORT = "БД"
    DESIGN = "проектирование"
    OPTIMIZATION = "оптимизация"
    NETWORKS = "сети"
    PROTOCOLS = "протоколы"
    STORAGE = "хранение данных"
    UNITS = "единицы измерения"
    LOGIC_TAG = "логика"

class DifficultyLevel(BaseStrEnum):
    EASY = 'Easy'
    MEDIUM = 'Medium'
    HARD = 'Hard'


class Achievement(BaseStrEnum):
    FIRST_WIN = "First_win"  # Первая победа в PvP
    FIRST_STEP = "First_step"  # Решена первая задача
    PROFILE_MASTER = "Profile_master"  # Установлена аватарка

    TASK_MASTER = "Task_master"  # Решено 100 задач
    KNOWLEDGE_TITAN = "Knowledge_titan"  # Решено 500 задач
    CENTURION = "Centurion"  # 100 побед в PvP

    SPEEDRUNNER = "Speedrunner"  # Решена задача быстрее чем за 5 секунд
    INTELLECTUAL = "Intellectual"  # Решено 5 задач уровня Hard подряд без ошибок
    INVINCIBLE = "Invincible"  # Серия из 10 побед в PvP без поражений

    PROGRAMMING_GURU = "Programming_guru"  # Решено 10 задач по программированию
    MATH_WIZARD = "Math_wizard"  # Решено 20 задач по математике
    LOGIC_KING = "Logic_king"  # Пройдены все темы категории Логика

    EARLY_BIRD = "Early_bird"  # Решена задача в период с 4 до 7 утра
    STREAK_7 = "Streak_7"  # Заходил 7 дней подряд


class RankName(BaseStrEnum):
    BRONZE = "Бронза"
    SILVER = "Серебро"
    GOLD = "Золото"
    ELITE = "Элита"
    SENSEI = "Сенсей"
    LEGEND = "Легенда"


SUBJECT_TO_TAGS = {
    Subject.MATH: [
        Tag.ALGEBRA, Tag.GEOMETRY, Tag.PROBABILITY, Tag.TRIGONOMETRY,
        Tag.AREA, Tag.STEREOMETRY, Tag.VOLUME, Tag.COMBINATORICS,
        Tag.NUMBERS, Tag.EQUATIONS, Tag.LOGARITHMS, Tag.ARITHMETIC
    ],
    Subject.PHYSICS: [
        Tag.ELECTRICITY, Tag.LAWS, Tag.SPACE, Tag.LIGHT,
        Tag.DYNAMICS, Tag.FORCES, Tag.MECHANICS, Tag.ENERGY
    ],
    Subject.ALGORITHMS: [
        Tag.SEQUENCES, Tag.SORTING, Tag.GRAPHS, Tag.RECURSION,
        Tag.SEARCH, Tag.DATA_STRUCTURES, Tag.OPTIMIZATION,Tag.LOGARITHMS,
        Tag.MEMORY,Tag.TERMINOLOGY
    ],
    Subject.INFORMATICS: [
        Tag.BASICS, Tag.NUMBER_SYSTEMS, Tag.TERMINOLOGY,
        Tag.MEMORY, Tag.BOOLEAN_ALGEBRA, Tag.NETWORKS, Tag.PROTOCOLS,
        Tag.STORAGE, Tag.UNITS, Tag.LOGIC_TAG, Tag.DB_SHORT, Tag.DESIGN
    ],
    Subject.DATABASES: [Tag.SQL_BASICS, Tag.DB_SHORT, Tag.DESIGN],
    Subject.PYTHON: [Tag.ASYNC, Tag.DECORATORS, Tag.OOP, Tag.DATA_TYPES],
    Subject.WEB_DEV: [Tag.HTML_CSS, Tag.REACT, Tag.FASTAPI],
    Subject.LOGIC: [Tag.SEQUENCES, Tag.SORTING, Tag.GRAPHS, Tag.RECURSION],
    Subject.CHEMISTRY: [],
    Subject.ENGLISH: [],
}