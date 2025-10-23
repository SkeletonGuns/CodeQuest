from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from . import models, auth, schemas
from typing import List, Optional


# --- Пользователи ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_create_schema: schemas.UserCreate, hashed_password: str):
    # Убедимся, что XP по умолчанию 0
    user = models.User(
        name=user_create_schema.name,
        last_name=user_create_schema.last_name,
        email=user_create_schema.email,
        password=hashed_password,
        role=user_create_schema.role,
        total_xp=0  # Устанавливаем начальный XP
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- Задачи (Tasks) ---

def get_task_by_id(db: Session, task_id: int):
    """Возвращает задачу по её ID."""
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_completed_task_ids_by_user(db: Session, user_id: int) -> List[int]:
    """Возвращает список ID задач, выполненных пользователем."""
    results = db.query(models.UserTask.task_id).filter(models.UserTask.user_id == user_id).all()
    return [r[0] for r in results]

def create_task(db: Session, task_schema: schemas.TaskCreate):
    """Создает новую задачу по программированию."""
    # Используем **task_schema.model_dump() для передачи всех полей из Pydantic схемы
    # в модель SQLAlchemy.
    # Это гарантирует, что все поля, включая 'language', будут доступны.
    db_task = models.Task(**task_schema.model_dump())

    # ПРИМЕЧАНИЕ: Если вы используете старую версию Pydantic (до v2), замените .model_dump()
    # на .dict() или .json(). Но .model_dump() - это стандарт Pydantic v2.
    # Если вы хотите явное определение, используйте:
    # db_task = models.Task(
    #    title=task_schema.title,
    #    description=task_schema.description,
    #    category=task_schema.category,
    #    xp_reward=task_schema.xp_reward,
    #    language=task_schema.language,
    #    test_cases=task_schema.test_cases,
    # )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_all_tasks(db: Session):
    """Возвращает список всех задач."""
    return db.query(models.Task).all()


def get_tasks_by_user_id(db: Session, user_id: int):
    """Возвращает список задач, выполненных пользователем."""
    return db.query(models.Task).join(models.UserTask).filter(models.UserTask.user_id == user_id).all()


def is_task_completed(db: Session, user_id: int, task_id: int) -> bool:
    """Проверяет, выполнил ли пользователь задачу."""
    return db.query(models.UserTask).filter(
        models.UserTask.user_id == user_id,
        models.UserTask.task_id == task_id
    ).first() is not None


def complete_task(db: Session, user_id: int, task_id: int):
    """Отмечает задачу как выполненную и начисляет XP."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not user or not task:
        return {"success": False, "message": "Пользователь или задача не найдены."}

    if is_task_completed(db, user_id, task_id):
        return {"success": False, "message": f"Задача '{task.title}' уже была выполнена ранее."}

    # Создание записи о выполнении
    user_task_completion = models.UserTask(user_id=user_id, task_id=task_id)
    db.add(user_task_completion)

    # Начисление XP
    user.total_xp += task.xp_reward

    db.commit()

    # Расчет уровня (логика в модели User, но мы можем обновить ее здесь для наглядности)
    new_level = user.total_xp // 1000

    return {"success": True,
            "message": f"Задача '{task.title}' выполнена! Получено {task.xp_reward} XP. Ваш новый уровень: {new_level}"}


# --- Достижения (Achievements) ---

def create_achievement(db: Session, achievement_schema: schemas.AchievementCreate):
    """Создает новое достижение (используется админом)."""
    db_achievement = models.Achievement(
        title=achievement_schema.title,
        description=achievement_schema.description,
        xp_bonus=achievement_schema.xp_bonus
    )
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement


# --- Чат (Messages) ---

def send_message(db: Session, user_id: int, content: str):
    """Отправляет новое сообщение в чат."""
    message = models.Message(
        user_id=user_id,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_recent_messages(db: Session, limit: int = 50) -> List[models.Message]:
    """Возвращает последние сообщения из чата, присоединяя информацию о пользователе."""
    return db.query(models.Message).options(joinedload(models.Message.user)).order_by(
        models.Message.timestamp.desc()).limit(limit).all()
