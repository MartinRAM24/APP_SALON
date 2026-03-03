import os
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import Base, engine, get_db
from app.models import Servicio, UserRole, Usuario
from app.routes import admin, auth, cliente

app = FastAPI(title="Salon App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")
templates = Jinja2Templates(directory=str(base_dir / "templates"))

app.include_router(auth.router)
app.include_router(cliente.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/panel", response_class=HTMLResponse)
def panel(request: Request, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    servicios = db.query(Servicio).order_by(Servicio.nombre.asc()).all()
    return templates.TemplateResponse(
        "panel.html",
        {
            "request": request,
            "rol": current_user.rol.value,
            "servicios": servicios,
            "is_admin": current_user.rol == UserRole.admin,
        },
    )
