from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, hash_password
from app.database import get_db
from app.models import UserRole, Usuario
from app.schemas import LoginInput, Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def register(payload: UsuarioCreate, db: Session = Depends(get_db)):
    exists = db.query(Usuario).filter(or_(Usuario.email == payload.email.lower(), Usuario.telefono == payload.telefono)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email o teléfono ya está registrado")

    user = Usuario(
        nombre=payload.nombre,
        telefono=payload.telefono,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        rol=UserRole.cliente,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.login, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token(str(user.id))
    return Token(access_token=token)
