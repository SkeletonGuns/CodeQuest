from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# --- КОНФИГУРАЦИЯ POSTGRESQL ---
# Используйте переменные окружения для безопасного хранения учетных данных.
# Если переменные не установлены, используются значения по умолчанию (для локального тестирования).

POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "123456")
POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "fastapi_base") # Замените на имя вашей БД

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True # Помогает поддерживать соединение
)

# Используем тот же SessionLocal, но он теперь связан с PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
