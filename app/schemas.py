from datetime import date, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import AppointmentStatus, UserRole


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    telefono: str = Field(min_length=7, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6, max_length=120)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    telefono: str
    email: EmailStr
    rol: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginInput(BaseModel):
    login: str
    password: str


class ServicioBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    duracion_minutos: int = Field(ge=15, le=480)
    precio: Decimal = Field(gt=0)


class ServicioCreate(ServicioBase):
    pass


class ServicioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    duracion_minutos: int | None = Field(default=None, ge=15, le=480)
    precio: Decimal | None = Field(default=None, gt=0)


class ServicioOut(ServicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CitaCreate(BaseModel):
    servicio_id: int
    fecha: date
    hora: time


class CitaCreateAdmin(CitaCreate):
    usuario_id: UUID


class CitaUpdateAdmin(BaseModel):
    servicio_id: int | None = None
    fecha: date | None = None
    hora: time | None = None
    estado: AppointmentStatus | None = None


class CitaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: UUID
    usuario_nombre: str
    servicio_id: int
    servicio_nombre: str
    fecha: date
    hora: time
    estado: AppointmentStatus


class DashboardCliente(BaseModel):
    proxima_cita: CitaOut | None
    historial: list[CitaOut]
    citas_hoy: int


class DashboardAdmin(BaseModel):
    proxima_cita: CitaOut | None
    citas: list[CitaOut]
    total: int
    page: int
    per_page: int
    citas_hoy: int
