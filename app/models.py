import enum
import uuid
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Time, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    cliente = "cliente"
    admin = "admin"


class AppointmentStatus(str, enum.Enum):
    agendada = "agendada"
    cancelada = "cancelada"
    completada = "completada"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(120), nullable=False)
    telefono = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(UserRole), nullable=False, default=UserRole.cliente)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    citas = relationship("Cita", back_populates="usuario", cascade="all,delete")


class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False, unique=True)
    duracion_minutos = Column(Integer, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)

    citas = relationship("Cita", back_populates="servicio")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.agendada)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="citas")
    servicio = relationship("Servicio", back_populates="citas")


Index("idx_citas_fecha_hora", Cita.fecha, Cita.hora)
