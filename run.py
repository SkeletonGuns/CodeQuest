# run.py
from app.main import app
from app.database import engine
from app import models

# Создаём таблицы после импорта всех моделей
models.Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True)