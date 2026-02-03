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
    GEOMETRY = "Геометрия"
    PROBABILITY_THEORY = "Теория Вероятностей"
    QUANTUM_PHYSICS = "Квантовая Физика"
    BIOINFORMATICS = "Биоинформатика"
    GAME_THEORY = "Теория Игр"
    TOPOLOGY = "Топология"
    ASTROPHYSICS = "Астрофизика"
    NETWORKS_SUBJ = "Сети"
    CRYPTOGRAPHY = "Криптография"
    LINGUISTICS = "Лингвистика"
    DISCRETE_MATH = "Дискретная Математика"
    NUCLEAR_PHYSICS = "Ядерная Физика"
    HARDWARE = "Железо"
    CHESS = "Шахматы"
    WEB = "Web"
    MNEMONICS = "Мнемоника"
    ASTRONOMY = "Астрономия"
    GEOGRAPHY = "География"
    IT_HISTORY = "История It" # Оставлено так, чтобы совпало с ошибкой в БД
    LITERATURE = "Литература"
    BIOLOGY = "Биология"
    SPORT = "Спорт"
    GENERAL_KNOWLEDGE = "Общие Знания"
    MYTHOLOGY = "Мифология"
    ECONOMICS = "Экономика"

class Tag(BaseStrEnum):
    ALGEBRA = "Алгебра"
    GEOMETRY = "Геометрия"
    PROBABILITY = "Теория Вероятностей"
    TRIGONOMETRY = "Тригонометрия"
    ASYNC = "Асинхронность"
    DECORATORS = "Декораторы"
    OOP = "Ооп"
    DATA_TYPES = "Типы Данных"
    HTML_CSS = "Html/Css"
    REACT = "React"
    FASTAPI = "Fastapi"
    SQL_BASICS = "Основы Sql"
    SEQUENCES = "Последовательности"
    SORTING = "Сортировки"
    GRAPHS = "Графы"
    RECURSION = "Рекурсия"
    ELECTRICITY = "Электричество"
    LAWS = "Законы"
    SPACE = "Космос"
    LIGHT = "Свет"
    DYNAMICS = "Динамика"
    FORCES = "Силы"
    MECHANICS = "Механика"
    ENERGY = "Энергия"
    AREA = "Площадь"
    STEREOMETRY = "Стереометрия"
    VOLUME = "Объем"
    COMBINATORICS = "Комбинаторика"
    NUMBERS = "Числа"
    EQUATIONS = "Уравнения"
    LOGARITHMS = "Логарифмы"
    ARITHMETIC = "Арифметика"
    SEARCH = "Поиск"
    DATA_STRUCTURES = "Структуры Данных"
    MEMORY = "Память"
    TERMINOLOGY = "Терминология"
    NUMBER_SYSTEMS = "Системы Счисления"
    BASICS = "Основы"
    BOOLEAN_ALGEBRA = "Булева Алгебра"
    DB_SHORT = "Бд"
    DESIGN = "Проектирование"
    OPTIMIZATION = "Оптимизация"
    NETWORKS = "Сети"
    PROTOCOLS = "Протоколы"
    STORAGE = "Хранение Данных"
    UNITS = "Единицы Измерения"
    LOGIC_TAG = "Логика"
    ALGORITHMS_TAG = "Алгоритмы"
    ANGLES = "Углы"
    PARADOXES = "Парадоксы"
    STATISTICS = "Статистика"
    QUANTA = "Кванты"
    BIOLOGY_TAG = "Биология"
    STRINGS = "Строки"
    ESOLANG = "Esolang"
    ECONOMICS_TAG = "Экономика"
    STRATEGY = "Стратегия"
    MATH_TAG = "Математика"
    NETWORK_TAG = "Network"
    SECURITY = "Безопасность"
    ERRORS = "Ошибки"
    DEVELOPMENT = "Разработка"
    LANGUAGES = "Языки"
    PATTERNS = "Шаблоны"
    BIG_O = "Bigo"
    COLORING = "Раскраска"
    CHEMISTRY_TAG = "Химия"
    DECAY = "Распад"
    BYTES = "Байты"
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
    SHAPES = "Фигуры"
    LEGENDS = "Легенды"
    CULTURE = "Культура"
    OPTICS = "Оптика"
    SOFT = "Софт"
    INTERNET = "Интернет"
    ATTENTIVENESS = "Внимательность"
    MONEY = "Деньги"
    RUSSIA = "Россия"
    FUNDAMENTAL = "Фундаментально"
    INFORMATICS_TAG = "Информатика"
    HARDWARE_TAG = "Железо"

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

# Карта разрешенных тегов (РАСШИРЕННАЯ, чтобы не падал валидатор)
SUBJECT_TO_TAGS = {
    Subject.MATH: [Tag.ALGEBRA, Tag.GEOMETRY, Tag.PROBABILITY, Tag.TRIGONOMETRY, Tag.AREA, Tag.STEREOMETRY, Tag.VOLUME, Tag.COMBINATORICS, Tag.NUMBERS, Tag.EQUATIONS, Tag.LOGARITHMS, Tag.ARITHMETIC, Tag.MATH_TAG, Tag.SHAPES, Tag.LOGIC_TAG, Tag.PARADOXES, Tag.STATISTICS],
    Subject.GEOMETRY: [Tag.GEOMETRY, Tag.ANGLES, Tag.SHAPES, Tag.MATH_TAG, Tag.FILES],
    Subject.PYTHON: [Tag.ASYNC, Tag.DECORATORS, Tag.OOP, Tag.DATA_TYPES, Tag.ALGORITHMS_TAG, Tag.NUMBERS, Tag.ERRORS, Tag.DEVELOPMENT, Tag.ESOLANG, Tag.STRINGS],
    Subject.INFORMATICS: [Tag.BASICS, Tag.NUMBER_SYSTEMS, Tag.TERMINOLOGY, Tag.MEMORY, Tag.BOOLEAN_ALGEBRA, Tag.NETWORKS, Tag.PROTOCOLS, Tag.STORAGE, Tag.UNITS, Tag.LOGIC_TAG, Tag.DB_SHORT, Tag.DESIGN, Tag.PC, Tag.BYTES, Tag.WINDOWS, Tag.FILES, Tag.SOFT, Tag.INTERNET, Tag.IT, Tag.HARDWARE_TAG, Tag.INFORMATICS_TAG, Tag.BIG_O, Tag.SORTING],
    Subject.PHYSICS: [Tag.ELECTRICITY, Tag.LAWS, Tag.SPACE, Tag.LIGHT, Tag.DYNAMICS, Tag.FORCES, Tag.MECHANICS, Tag.ENERGY, Tag.SUBSTANCE, Tag.PROCESSES, Tag.OPTICS, Tag.FUNDAMENTAL, Tag.QUANTA],
    Subject.ALGORITHMS: [Tag.SEQUENCES, Tag.SORTING, Tag.GRAPHS, Tag.RECURSION, Tag.SEARCH, Tag.DATA_STRUCTURES, Tag.OPTIMIZATION, Tag.LOGARITHMS, Tag.MEMORY, Tag.TERMINOLOGY, Tag.BIG_O, Tag.ALGORITHMS_TAG, Tag.INFORMATICS_TAG],
    Subject.LOGIC: [Tag.SEQUENCES, Tag.SORTING, Tag.GRAPHS, Tag.RECURSION, Tag.LOGIC_TAG, Tag.PHILOSOPHY, Tag.PREDICATES, Tag.CALENDAR, Tag.ATTENTIVENESS, Tag.PARADOXES],
    Subject.TOPOLOGY: [Tag.MATH_TAG, Tag.GEOMETRY],
    Subject.CHEMISTRY: [Tag.BASIC, Tag.SUBSTANCES, Tag.CHEMISTRY_TAG, Tag.DECAY, Tag.SUBSTANCE],
    Subject.DATABASES: [Tag.SQL_BASICS, Tag.DB_SHORT, Tag.DESIGN, Tag.SQL, Tag.DATA],
    Subject.PROBABILITY_THEORY: [Tag.LOGIC_TAG, Tag.PARADOXES, Tag.STATISTICS, Tag.PROBABILITY],
    Subject.QUANTUM_PHYSICS: [Tag.QUANTA, Tag.INFORMATICS_TAG],
    Subject.BIOINFORMATICS: [Tag.BIOLOGY_TAG, Tag.STRINGS],
    Subject.GAME_THEORY: [Tag.ECONOMICS_TAG, Tag.STRATEGY, Tag.GAMES],
    Subject.ASTROPHYSICS: [Tag.SPACE, Tag.LOGARITHMS, Tag.PLANETS],
    Subject.NETWORKS_SUBJ: [Tag.NETWORK_TAG, Tag.INFORMATICS_TAG],
    Subject.CRYPTOGRAPHY: [Tag.SECURITY, Tag.NUMBERS],
    Subject.LINGUISTICS: [Tag.LANGUAGES, Tag.PATTERNS],
    Subject.DISCRETE_MATH: [Tag.GRAPHS, Tag.COLORING],
    Subject.NUCLEAR_PHYSICS: [Tag.CHEMISTRY_TAG, Tag.DECAY, Tag.SUBSTANCE],
    Subject.HARDWARE: [Tag.BYTES, Tag.MEMORY, Tag.PC, Tag.HARDWARE_TAG],
    Subject.CHESS: [Tag.GAMES, Tag.CHESS_TAG],
    Subject.WEB: [Tag.HTTP, Tag.BACKEND],
    Subject.MNEMONICS: [Tag.NUMBERS, Tag.MEMORY],
    Subject.ASTRONOMY: [Tag.SPACE, Tag.PLANETS],
    Subject.GEOGRAPHY: [Tag.CITIES, Tag.EUROPE, Tag.NAVIGATION, Tag.EARTH],
    Subject.IT_HISTORY: [Tag.IT, Tag.PERSONALITIES],
    Subject.LITERATURE: [Tag.CARTOONS, Tag.CLASSICS],
    Subject.BIOLOGY: [Tag.NATURE, Tag.ANIMALS, Tag.BIOLOGY_TAG],
    Subject.SPORT: [Tag.OLYMPIAD, Tag.SYMBOLS],
    Subject.GENERAL_KNOWLEDGE: [Tag.CALENDAR, Tag.NATURE],
    Subject.MYTHOLOGY: [Tag.LEGENDS, Tag.CULTURE],
    Subject.ECONOMICS: [Tag.MONEY, Tag.RUSSIA, Tag.ECONOMICS_TAG],
}