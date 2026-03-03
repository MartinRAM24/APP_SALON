"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, hash_password
from app.database import get_db
from app.models import User
from app.schemas import LoginData, Token, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(or_(User.email == user_data.email, User.telefono == user_data.telefono)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email o teléfono ya están registrados.")

    user = User(
        nombre=user_data.nombre,
        telefono=user_data.telefono,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        rol="cliente",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginData, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.identifier, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    token = create_access_token(str(user.id), user.rol)
    return Token(access_token=token)
