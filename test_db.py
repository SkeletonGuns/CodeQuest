import os
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:123456@localhost/project_fastAPI"

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print("❌ Ошибка подключения:", e)