from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import AppointmentStatus, Cita, Servicio, Usuario
from app.schemas import CitaCreate, CitaOut, DashboardCliente

router = APIRouter(prefix="/api/cliente", tags=["cliente"])


def _serialize(cita: Cita) -> CitaOut:
    return CitaOut(
        id=cita.id,
        usuario_id=cita.usuario_id,
        usuario_nombre=cita.usuario.nombre,
        servicio_id=cita.servicio_id,
        servicio_nombre=cita.servicio.nombre,
        fecha=cita.fecha,
        hora=cita.hora,
        estado=cita.estado,
    )


def _validar_agenda(db: Session, fecha: date, hora):
    hoy = date.today()
    if fecha <= hoy:
        raise HTTPException(status_code=400, detail="Las citas deben agendarse a partir de mañana")

    ocupada = db.query(Cita).filter(
        and_(Cita.fecha == fecha, Cita.hora == hora, Cita.estado == AppointmentStatus.agendada)
    ).first()
    if ocupada:
        raise HTTPException(status_code=400, detail="Ese horario ya está reservado")


@router.get("/dashboard", response_model=DashboardCliente)
def dashboard(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now()

    proxima = (
        db.query(Cita)
        .options(joinedload(Cita.usuario), joinedload(Cita.servicio))
        .filter(
            Cita.usuario_id == current_user.id,
            Cita.estado == AppointmentStatus.agendada,
            Cita.fecha >= now.date(),
        )
        .order_by(Cita.fecha.asc(), Cita.hora.asc())
        .first()
    )

    historial = (
        db.query(Cita)
        .options(joinedload(Cita.usuario), joinedload(Cita.servicio))
        .filter(Cita.usuario_id == current_user.id)
        .order_by(Cita.fecha.desc(), Cita.hora.desc())
        .all()
    )

    citas_hoy = db.query(func.count(Cita.id)).filter(Cita.usuario_id == current_user.id, Cita.fecha == now.date()).scalar() or 0

    return DashboardCliente(
        proxima_cita=_serialize(proxima) if proxima else None,
        historial=[_serialize(c) for c in historial],
        citas_hoy=citas_hoy,
    )


@router.post("/citas", response_model=CitaOut, status_code=status.HTTP_201_CREATED)
def crear_cita(
    payload: CitaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    servicio = db.query(Servicio).filter(Servicio.id == payload.servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    _validar_agenda(db, payload.fecha, payload.hora)

    cita = Cita(
        usuario_id=current_user.id,
        servicio_id=payload.servicio_id,
        fecha=payload.fecha,
        hora=payload.hora,
        estado=AppointmentStatus.agendada,
    )
    db.add(cita)
    db.commit()
    db.refresh(cita)
    db.refresh(current_user)
    cita.usuario = current_user
    cita.servicio = servicio
    return _serialize(cita)
