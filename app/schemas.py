from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- АУТЕНТИКАЦИЯ ---

class Token(BaseModel):
    """Схема для ответа после успешного входа."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема для данных внутри JWT-токена."""
    email: Optional[str] = None


# --- ПОЛЬЗОВАТЕЛЬСКИЕ СХЕМЫ ---

class UserBase(BaseModel):
    """Общие поля для пользователя."""
    email: EmailStr
    name: str
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания нового пользователя (регистрации)."""
    password: str
    role: str = "user"  # Добавляем роль по умолчанию


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя."""
    bio: Optional[str] = None
    avatar: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None


class User(UserBase):
    """Схема для возврата данных пользователя (скрываем пароль)."""
    id: int
    role: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    total_xp: int
    created_at: datetime

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


# --- СХЕМЫ ЗАДАЧ (Task) ---

class TaskCreate(BaseModel):
    """Схема для создания новой задачи."""
    title: str
    description: Optional[str] = None
    difficulty: str = "Другое"
    xp_reward: int = 10


class Task(TaskCreate):
    """Схема для отображения задачи."""
    id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- ПРОЧИЕ СХЕМЫ (для Application, если нужно) ---
class ApplicationCreate(BaseModel):
    """Схема для создания заявки."""
    nickname: str
    name: str
    email: EmailStr
    password: str


class Application(ApplicationCreate):
    """Схема для отображения заявки."""
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AchievementBase(BaseModel):
    title: str
    description: str
    xp_bonus: int = 0


class AchievementCreate(AchievementBase):
    pass


class Achievement(AchievementBase):
    id: int

    class Config:
        from_attributes = True


# --- Сообщения Чата (НОВЫЕ СХЕМЫ) ---

class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True