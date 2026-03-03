"""Pydantic schemas for requests and responses."""

from datetime import date, datetime, time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    telefono: str = Field(min_length=7, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    telefono: str
    email: EmailStr
    rol: str
    created_at: datetime


class LoginData(BaseModel):
    identifier: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str


class ServiceBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    duracion_minutos: int = Field(gt=0, le=600)
    precio: float = Field(gt=0)


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    duracion_minutos: int | None = Field(default=None, gt=0, le=600)
    precio: float | None = Field(default=None, gt=0)


class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AppointmentCreate(BaseModel):
    servicio_id: int
    fecha: date
    hora: time


class AppointmentAdminCreate(AppointmentCreate):
    usuario_id: UUID


class AppointmentUpdate(BaseModel):
    servicio_id: int | None = None
    fecha: date | None = None
    hora: time | None = None
    estado: Literal["agendada", "cancelada", "completada"] | None = None


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: UUID
    usuario_nombre: str
    servicio_id: int
    servicio_nombre: str
    fecha: date
    hora: time
    estado: str
    created_at: datetime


class AdminClientMatch(BaseModel):
    id: UUID
    nombre: str
    telefono: str
    email: EmailStr
