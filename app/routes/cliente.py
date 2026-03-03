"""Client dashboard and appointment operations."""

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Appointment, Service, User
from app.schemas import AppointmentCreate, AppointmentOut, ServiceOut

router = APIRouter(prefix="/api/cliente", tags=["cliente"])


def validate_appointment_slot(db: Session, fecha: date, hora, exclude_id: int | None = None):
    today = date.today()
    if fecha <= today:
        raise HTTPException(status_code=400, detail="Solo puedes agendar a partir de mañana.")

    query = db.query(Appointment).filter(
        Appointment.fecha == fecha,
        Appointment.hora == hora,
        Appointment.estado == "agendada",
    )
    if exclude_id is not None:
        query = query.filter(Appointment.id != exclude_id)
    conflict = query.first()
    if conflict:
        raise HTTPException(status_code=400, detail="Ese horario ya está reservado.")


@router.get("/servicios", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).order_by(Service.nombre.asc()).all()


@router.post("/citas", response_model=AppointmentOut)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = db.query(Service).filter(Service.id == payload.servicio_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")

    validate_appointment_slot(db, payload.fecha, payload.hora)

    appointment = Appointment(
        usuario_id=user.id,
        servicio_id=payload.servicio_id,
        fecha=payload.fecha,
        hora=payload.hora,
        estado="agendada",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return AppointmentOut(
        id=appointment.id,
        usuario_id=appointment.usuario_id,
        usuario_nombre=user.nombre,
        servicio_id=appointment.servicio_id,
        servicio_nombre=appointment.servicio.nombre,
        fecha=appointment.fecha,
        hora=appointment.hora,
        estado=appointment.estado,
        created_at=appointment.created_at,
    )


@router.get("/citas", response_model=list[AppointmentOut])
def get_my_appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointments = (
        db.query(Appointment)
        .join(Service)
        .filter(Appointment.usuario_id == user.id)
        .order_by(Appointment.fecha.asc(), Appointment.hora.asc())
        .all()
    )

    return [
        AppointmentOut(
            id=item.id,
            usuario_id=item.usuario_id,
            usuario_nombre=user.nombre,
            servicio_id=item.servicio_id,
            servicio_nombre=item.servicio.nombre,
            fecha=item.fecha,
            hora=item.hora,
            estado=item.estado,
            created_at=item.created_at,
        )
        for item in appointments
    ]


@router.get("/resumen")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now()
    next_appointment = (
        db.query(Appointment)
        .join(Service)
        .filter(
            Appointment.usuario_id == user.id,
            Appointment.estado == "agendada",
            and_(
                Appointment.fecha > now.date(),
            )
            | and_(Appointment.fecha == now.date(), Appointment.hora > now.time()),
        )
        .order_by(Appointment.fecha.asc(), Appointment.hora.asc())
        .first()
    )

    today_count = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.usuario_id == user.id, Appointment.fecha == date.today(), Appointment.estado == "agendada")
        .scalar()
    )

    return {
        "proxima_cita": (
            {
                "id": next_appointment.id,
                "servicio": next_appointment.servicio.nombre,
                "fecha": next_appointment.fecha.isoformat(),
                "hora": next_appointment.hora.strftime("%H:%M"),
            }
            if next_appointment
            else None
        ),
        "citas_hoy": today_count,
    }
