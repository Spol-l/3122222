from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from models import User
from schemas import RegisterRequest, LoginRequest
from dependencies import get_db


router = APIRouter(
    prefix="/api",
    tags=["Authentication"]
)


# =========================
# РЕГИСТРАЦИЯ
# =========================

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Проверяем, есть ли пользователь
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует."
        )

    # Создаём пользователя
    new_user = User(
        name=data.name,
        email=data.email,
        password=data.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "message": "Регистрация прошла успешно!",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


# =========================
# ВХОД
# =========================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    # Ищем пользователя В БАЗЕ
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    # Пользователя нет
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден. Сначала зарегистрируйтесь."
        )

    # Проверяем пароль
    if user.password != data.password:
        raise HTTPException(
            status_code=401,
            detail="Неверный пароль."
        )

    # Всё правильно
    return {
        "success": True,
        "message": "Вход выполнен успешно!",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }