from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func, ForeignKey, event
from sqlalchemy.future import engine
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from .database import Base

# Константа для расчета уровня
XP_PER_LEVEL = 1000


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # обязательное имя (никнейма больше нет)
    last_name = Column(String)  # фамилия (опционально)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")  # user или admin
    bio = Column(Text)
    avatar = Column(String)  # путь к аватару
    total_xp = Column(Integer, default=0)  # общий опыт
    created_at = Column(DateTime, default=func.now())

    # Вычисляемое свойство для уровня
    # 1 уровень = 1000 XP. 0-999 XP = 1 уровень, 1000-1999 XP = 2 уровень и т.д.
    @hybrid_property
    def level(self):
        # Используем max(1, ...) чтобы минимальный уровень был 1
        return max(1, self.total_xp // XP_PER_LEVEL + 1)

    # Отношения
    tasks = relationship("Task", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    quests = relationship("UserQuest", back_populates="user")
    messages = relationship("Message", back_populates="user")


class UserTask(Base):
    """Модель для отслеживания выполненных пользователем задач."""
    __tablename__ = "user_tasks"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    completed_at = Column(DateTime, default=func.now())

    # Отношения
    user = relationship("User")
    task = relationship("Task")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Пользователь, который взял задачу
    title = Column(String)
    description = Column(Text, nullable=True)
    difficulty = Column(String, default="Другое")
    xp_reward = Column(Integer, default=100)  # Увеличил награду, чтобы соответствовало 1000 XP за уровень
    is_completed = Column(Boolean, default=False)

    # Дополнительные поля для задач по программированию
    language = Column(String, default="Python")  # Язык программирования (Python, JavaScript и т.д.)
    test_cases = Column(Text, nullable=True)  # JSON или текст с тестовыми примерами

    user = relationship("User", back_populates="tasks")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    description = Column(Text)
    xp_bonus = Column(Integer, default=0)  # Дополнительный XP за достижение

    users = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), primary_key=True)
    granted_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")


class Quest(Base):
    __tablename__ = "quests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    xp_reward = Column(Integer, default=500)

    users = relationship("UserQuest", back_populates="quest")


class UserQuest(Base):
    __tablename__ = "user_quests"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="quests")
    quest = relationship("Quest", back_populates="users")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="messages")