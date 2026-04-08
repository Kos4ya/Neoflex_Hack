from enum import Enum


class SessionStatus(str, Enum):
    """Статусы сессии интервью"""
    SCHEDULED = "scheduled"      # Запланирована
    ACTIVE = "active"             # В процессе
    PAUSED = "paused"             # На паузе
    COMPLETED = "completed"       # Завершена
    CANCELLED = "cancelled"       # Отменена
    EXPIRED = "expired"           # Истекла


class Language(str, Enum):
    """Языки программирования"""
    PYTHON = "python"
    KOTLIN = "kotlin"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"


class MetricName(str, Enum):
    """Названия метрик"""
    FIRST_ACTION_TIME = "first_action_time"
    INACTIVITY_PERIOD = "inactivity_period"
    LARGE_PASTE = "large_paste"
    TYPING_SPEED = "typing_speed"
    BACKSPACE_FREQUENCY = "backspace_frequency"
    CODE_SIMILARITY_SCORE = "code_similarity_score"


class Severity(str, Enum):
    """Уровень серьезности метрики"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"