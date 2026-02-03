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
    # Предметы в строгом соответствии с твоей БД (Initcap)
    PYTHON = "Python"
    GEOMETRY = "Геометрия"
    INFORMATICS = "Информатика"
    PROBABILITY_THEORY = "Теория Вероятностей"
    QUANTUM_PHYSICS = "Квантовая Физика"
    BIOINFORMATICS = "Биоинформатика"
    GAME_THEORY = "Теория Игр"
    TOPOLOGY = "Топология"
    ASTROPHYSICS = "Астрофизика"
    NETWORKS_SUBJ = "Сети"
    CRYPTOGRAPHY = "Криптография"
    LINGUISTICS = "Лингвистика"
    ALGORITHMS = "Алгоритмы"
    DISCRETE_MATH = "Дискретная Математика"
    NUCLEAR_PHYSICS = "Ядерная Физика"
    HARDWARE = "Железо"
    LOGIC = "Логика"
    CHESS = "Шахматы"
    DATABASES = "Базы Данных"
    WEB = "Web"
    MNEMONICS = "Мнемоника"
    CHEMISTRY = "Химия"
    ASTRONOMY = "Астрономия"
    MATH = "Математика"
    GEOGRAPHY = "География"
    IT_HISTORY = "История It"
    PHYSICS = "Физика"
    LITERATURE = "Литература"
    BIOLOGY = "Биология"
    SPORT = "Спорт"
    GENERAL_KNOWLEDGE = "Общие Знания"
    MYTHOLOGY = "Мифология"
    ECONOMICS = "Экономика"
    # Дополнительные (из прошлых версий)
    WEB_DEV = "Web-Разработка"
    ENGLISH = "Английский Язык"

class Tag(BaseStrEnum):
    # Добавлены недостающие атрибуты из твоего лога (SPACE, LOGARITHMS и др.)
    ALGORITHMS_TAG = "Алгоритмы"
    NUMBERS = "Числа"
    GEOMETRY_TAG = "Геометрия"
    ANGLES = "Углы"
    NUM_SYSTEMS = "Системы Счисления"
    LOGIC_TAG = "Логика"
    PARADOXES = "Парадоксы"
    STATISTICS = "Статистика"
    QUANTA = "Кванты"
    INFORMATICS_TAG = "Информатика"
    BIOLOGY_TAG = "Биология"
    STRINGS = "Строки"
    ESOLANG = "Esolang"
    ECONOMICS_TAG = "Экономика"
    STRATEGY = "Стратегия"
    MATH_TAG = "Математика"
    SPACE = "Космос"
    LOGARITHMS = "Логарифмы"
    NETWORK = "Network"
    SECURITY = "Безопасность"
    ERRORS = "Ошибки"
    DEVELOPMENT = "Разработка"
    LANGUAGES = "Языки"
    PATTERNS = "Шаблоны"
    BIGO = "Bigo"
    SORTING = "Сортировки"
    GRAPHS = "Графы"
    COLORING = "Раскраска"
    CHEMISTRY_TAG = "Химия"
    DECAY = "Распад"
    BYTES = "Байты"
    MEMORY = "Память"
    PHILOSOPHY = "Философия"
    PREDICATES = "Предикаты"
    GAMES = "Игры"
    CHESS_TAG = "Шахматы"
    SQL = "Sql"
    DATA = "Data"
    HTTP = "Http"
    BACKEND = "Backend"
    BASIC = "Базовый"
    SUBSTANCES = "Вещества"
    PLANETS = "Планеты"
    CITIES = "Города"
    EUROPE = "Европа"
    IT = "It"
    PERSONALITIES = "Личности"
    SUBSTANCE = "Вещество"
    PROCESSES = "Процессы"
    CARTOONS = "Мультфильмы"
    CLASSICS = "Классика"
    HARDWARE_TAG = "Железо"
    PC = "Пк"
    NATURE = "Природа"
    ANIMALS = "Животные"
    OLYMPIAD = "Олимпиада"
    SYMBOLS = "Символы"
    CALENDAR = "Календарь"
    WINDOWS = "Windows"
    FILES = "Файлы"
    NAVIGATION = "Навигация"
    EARTH = "Земля"
    FIGURES = "Фигуры"
    LEGENDS = "Легенды"
    CULTURE = "Культура"
    LIGHT = "Свет"
    OPTICS = "Оптика"
    SOFT = "Софт"
    INTERNET = "Интернет"
    ATTENTIVENESS = "Внимательность"
    MONEY = "Деньги"
    RUSSIA = "Россия"
    FUNDAMENTAL = "Фундаментально"
    ENERGY = "Энергия"
    ARITHMETIC = "Арифметика"
    # Дополнительные
    ALGEBRA = "Алгебра"
    TRIGONOMETRY = "Тригонометрия"
    ASYNC = "Асинхронность"
    OOP = "Ооп"

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

# Карта связей согласно твоему списку из БД
SUBJECT_TO_TAGS = {
    Subject.PYTHON: [Tag.ALGORITHMS_TAG, Tag.NUMBERS, Tag.ESOLANG, Tag.ERRORS, Tag.DEVELOPMENT],
    Subject.GEOMETRY: [Tag.GEOMETRY_TAG, Tag.ANGLES, Tag.FIGURES, Tag.MATH_TAG],
    Subject.INFORMATICS: [Tag.NUM_SYSTEMS, Tag.HARDWARE_TAG, Tag.PC, Tag.WINDOWS, Tag.FILES, Tag.SOFT, Tag.INTERNET],
    Subject.PROBABILITY_THEORY: [Tag.LOGIC_TAG, Tag.PARADOXES, Tag.STATISTICS],
    Subject.QUANTUM_PHYSICS: [Tag.QUANTA, Tag.INFORMATICS_TAG],
    Subject.BIOINFORMATICS: [Tag.BIOLOGY_TAG, Tag.STRINGS],
    Subject.GAME_THEORY: [Tag.ECONOMICS_TAG, Tag.STRATEGY],
    Subject.TOPOLOGY: [Tag.MATH_TAG, Tag.GEOMETRY_TAG],
    Subject.ASTROPHYSICS: [Tag.SPACE, Tag.LOGARITHMS],
    Subject.NETWORKS_SUBJ: [Tag.NETWORK, Tag.INFORMATICS_TAG],
    Subject.CRYPTOGRAPHY: [Tag.SECURITY, Tag.NUMBERS],
    Subject.LINGUISTICS: [Tag.LANGUAGES, Tag.PATTERNS],
    Subject.ALGORITHMS: [Tag.BIGO, Tag.SORTING],
    Subject.DISCRETE_MATH: [Tag.GRAPHS, Tag.COLORING],
    Subject.NUCLEAR_PHYSICS: [Tag.CHEMISTRY_TAG, Tag.DECAY],
    Subject.HARDWARE: [Tag.BYTES, Tag.MEMORY],
    Subject.LOGIC: [Tag.PHILOSOPHY, Tag.PREDICATES, Tag.CALENDAR, Tag.ATTENTIVENESS],
    Subject.CHESS: [Tag.GAMES, Tag.CHESS_TAG],
    Subject.DATABASES: [Tag.SQL, Tag.DATA],
    Subject.WEB: [Tag.HTTP, Tag.BACKEND],
    Subject.MNEMONICS: [Tag.NUMBERS, Tag.MEMORY],
    Subject.CHEMISTRY: [Tag.BASIC, Tag.SUBSTANCES],
    Subject.ASTRONOMY: [Tag.SPACE, Tag.PLANETS],
    Subject.MATH: [Tag.ARITHMETIC, Tag.NUMBERS, Tag.MATH_TAG, Tag.GEOMETRY_TAG],
    Subject.GEOGRAPHY: [Tag.CITIES, Tag.EUROPE, Tag.NAVIGATION, Tag.EARTH],
    Subject.IT_HISTORY: [Tag.IT, Tag.PERSONALITIES],
    Subject.PHYSICS: [Tag.SUBSTANCE, Tag.PROCESSES, Tag.LIGHT, Tag.OPTICS, Tag.FUNDAMENTAL, Tag.ENERGY],
    Subject.LITERATURE: [Tag.CARTOONS, Tag.CLASSICS],
    Subject.BIOLOGY: [Tag.NATURE, Tag.ANIMALS],
    Subject.SPORT: [Tag.OLYMPIAD, Tag.SYMBOLS],
    Subject.GENERAL_KNOWLEDGE: [Tag.CALENDAR, Tag.NATURE],
    Subject.MYTHOLOGY: [Tag.LEGENDS, Tag.CULTURE],
    Subject.ECONOMICS: [Tag.MONEY, Tag.RUSSIA],
}