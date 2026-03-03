"""Main FastAPI application entrypoint."""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Service, User
from app.routes import admin, auth, cliente

app = FastAPI(title="Salon App", version="1.0.0")

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def resolve_logo_src() -> str:
    """Resolve logo source from env or local static files."""
    logo_url = os.getenv("LOGO_URL", "").strip()
    if logo_url:
        return logo_url

    if os.path.exists("static/logo.png"):
        return "/static/logo.png"

    return "/static/logo.svg"


app.include_router(auth.router)
app.include_router(cliente.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_phone = os.getenv("ADMIN_PHONE")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_name = os.getenv("ADMIN_NAME", "Dueña del salón")
        if admin_email and admin_phone and admin_password:
            exists = db.query(User).filter(User.email == admin_email).first()
            if not exists:
                if len(admin_password.encode("utf-8")) <= 72:
                    db.add(
                        User(
                            nombre=admin_name,
                            telefono=admin_phone,
                            email=admin_email,
                            password_hash=hash_password(admin_password),
                            rol="admin",
                        )
                    )
                else:
                    print("[startup] ADMIN_PASSWORD excede 72 bytes y no se creó usuario admin automático.")
        if not db.query(Service).first():
            db.add_all(
                [
                    Service(nombre="Corte + Peinado", duracion_minutos=60, precio=35.0),
                    Service(nombre="Manicure Premium", duracion_minutos=45, precio=25.0),
                    Service(nombre="Coloración Completa", duracion_minutos=120, precio=70.0),
                ]
            )
        db.commit()
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "logo_src": resolve_logo_src()})


@app.get("/cliente", response_class=HTMLResponse)
def cliente_panel(request: Request):
    return templates.TemplateResponse("cliente.html", {"request": request, "logo_src": resolve_logo_src()})


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "logo_src": resolve_logo_src()})
