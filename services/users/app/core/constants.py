from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    INTERVIEWER = "interviewer"
    MANAGER = "manager"
    ADMIN = "admin"


class Permission(str, Enum):
    """Разрешения"""
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"