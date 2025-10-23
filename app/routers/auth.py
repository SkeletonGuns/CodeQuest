# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import crud, auth, models, schemas
from ..database import get_db
import os
import shutil
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    db: Session = Depends(get_db)
):
    form = await request.form()
    nickname = form.get("nickname")
    name = form.get("name")
    email = form.get("email")
    password = form.get("password")
    confirm = form.get("confirm")

    if not all([nickname, name, email, password, confirm]):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Все поля обязательны"})
    if password != confirm:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пароли не совпадают"})

    if db.query(models.Application).filter(models.Application.email == email).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Заявка уже существует"})
    if db.query(models.User).filter(models.User.email == email).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})

    hashed = auth.hash_password(password)
    new_app = models.Application(
        nickname=nickname, name=name, email=email, password=hashed
    )
    db.add(new_app)
    db.commit()
    return RedirectResponse(url="/login?msg=Заявка отправлена", status_code=303)