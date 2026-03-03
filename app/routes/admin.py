from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_admin
from app.database import get_db
from app.models import AppointmentStatus, Cita, Servicio, Usuario
from app.schemas import CitaCreateAdmin, CitaOut, CitaUpdateAdmin, DashboardAdmin, ServicioCreate, ServicioOut, ServicioUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])


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


def _validar_agenda(db: Session, fecha, hora, cita_id: int | None = None):
    if fecha <= date.today():
        raise HTTPException(status_code=400, detail="Las citas deben agendarse desde mañana")
    query = db.query(Cita).filter(and_(Cita.fecha == fecha, Cita.hora == hora, Cita.estado == AppointmentStatus.agendada))
    if cita_id:
        query = query.filter(Cita.id != cita_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Ese horario ya está reservado")


@router.get("/dashboard", response_model=DashboardAdmin)
def dashboard(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    _: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    base = db.query(Cita).options(joinedload(Cita.usuario), joinedload(Cita.servicio)).order_by(Cita.fecha.asc(), Cita.hora.asc())

    proxima = (
        db.query(Cita)
        .options(joinedload(Cita.usuario), joinedload(Cita.servicio))
        .filter(Cita.estado == AppointmentStatus.agendada, Cita.fecha >= now.date())
        .order_by(Cita.fecha.asc(), Cita.hora.asc())
        .first()
    )

    total = base.count()
    citas = base.offset((page - 1) * per_page).limit(per_page).all()
    citas_hoy = db.query(func.count(Cita.id)).filter(Cita.fecha == now.date()).scalar() or 0
    return DashboardAdmin(
        proxima_cita=_serialize(proxima) if proxima else None,
        citas=[_serialize(c) for c in citas],
        total=total,
        page=page,
        per_page=per_page,
        citas_hoy=citas_hoy,
    )


@router.post("/citas", response_model=CitaOut, status_code=status.HTTP_201_CREATED)
def crear_cita_admin(payload: CitaCreateAdmin, _: Usuario = Depends(get_current_admin), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == payload.usuario_id).first()
    servicio = db.query(Servicio).filter(Servicio.id == payload.servicio_id).first()
    if not usuario or not servicio:
        raise HTTPException(status_code=404, detail="Usuario o servicio no encontrado")
    _validar_agenda(db, payload.fecha, payload.hora)

    cita = Cita(usuario_id=usuario.id, servicio_id=servicio.id, fecha=payload.fecha, hora=payload.hora)
    db.add(cita)
    db.commit()
    db.refresh(cita)
    cita.usuario = usuario
    cita.servicio = servicio
    return _serialize(cita)


@router.patch("/citas/{cita_id}", response_model=CitaOut)
def actualizar_cita(
    cita_id: int,
    payload: CitaUpdateAdmin,
    _: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    cita = db.query(Cita).options(joinedload(Cita.usuario), joinedload(Cita.servicio)).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    if payload.servicio_id:
        servicio = db.query(Servicio).filter(Servicio.id == payload.servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        cita.servicio_id = payload.servicio_id

    new_fecha = payload.fecha or cita.fecha
    new_hora = payload.hora or cita.hora
    if payload.fecha or payload.hora:
        _validar_agenda(db, new_fecha, new_hora, cita.id)
        cita.fecha = new_fecha
        cita.hora = new_hora

    if payload.estado:
        cita.estado = payload.estado

    db.commit()
    db.refresh(cita)
    return _serialize(cita)


@router.delete("/citas/{cita_id}")
def cancelar_cita(cita_id: int, _: Usuario = Depends(get_current_admin), db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    cita.estado = AppointmentStatus.cancelada
    db.commit()
    return {"message": "Cita cancelada"}


@router.get("/servicios", response_model=list[ServicioOut])
def listar_servicios(_: Usuario = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Servicio).order_by(Servicio.nombre.asc()).all()


@router.post("/servicios", response_model=ServicioOut, status_code=status.HTTP_201_CREATED)
def crear_servicio(payload: ServicioCreate, _: Usuario = Depends(get_current_admin), db: Session = Depends(get_db)):
    if db.query(Servicio).filter(Servicio.nombre == payload.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe un servicio con ese nombre")
    servicio = Servicio(**payload.model_dump())
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


@router.patch("/servicios/{servicio_id}", response_model=ServicioOut)
def editar_servicio(servicio_id: int, payload: ServicioUpdate, _: Usuario = Depends(get_current_admin), db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(servicio, key, value)
    db.commit()
    db.refresh(servicio)
    return servicio
