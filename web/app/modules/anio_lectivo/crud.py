from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.modules.anio_lectivo.models import AnioLectivo
from app.modules.anio_lectivo.schemas import AnioLectivoCreate, AnioLectivoUpdate


def get_anio_lectivo(db: Session, id_anio: UUID) -> Optional[AnioLectivo]:
    """
    Obtiene un año lectivo por su ID
    """
    return db.query(AnioLectivo).filter(AnioLectivo.id_anio == id_anio).first()


def get_anio_lectivo_by_nombre(db: Session, nombre: str) -> Optional[AnioLectivo]:
    """
    Obtiene un año lectivo por su nombre
    """
    return db.query(AnioLectivo).filter(AnioLectivo.nombre == nombre).first()


def get_anio_lectivo_activo(db: Session) -> Optional[AnioLectivo]:
    """
    Obtiene el año lectivo activo
    """
    return db.query(AnioLectivo).filter(AnioLectivo.activo == True).first()


def get_anios_lectivos(db: Session, skip: int = 0, limit: int = 100) -> List[AnioLectivo]:
    """
    Obtiene todos los años lectivos ordenados por fecha de inicio descendente
    """
    return db.query(AnioLectivo).order_by(desc(AnioLectivo.fecha_inicio)).offset(skip).limit(limit).all()


def create_anio_lectivo(db: Session, anio_lectivo: AnioLectivoCreate) -> AnioLectivo:
    """
    Crea un nuevo año lectivo
    """
    db_anio_lectivo = AnioLectivo(
        nombre=anio_lectivo.nombre,
        fecha_inicio=anio_lectivo.fecha_inicio,
        fecha_fin=anio_lectivo.fecha_fin,
        activo=anio_lectivo.activo
    )
    
    # Si este año lectivo se marca como activo, desactivar cualquier otro año activo
    if anio_lectivo.activo:
        db.query(AnioLectivo).filter(AnioLectivo.activo == True).update({"activo": False})
    
    db.add(db_anio_lectivo)
    db.commit()
    db.refresh(db_anio_lectivo)
    return db_anio_lectivo


def update_anio_lectivo(db: Session, id_anio: UUID, anio_lectivo: AnioLectivoUpdate) -> Optional[AnioLectivo]:
    """
    Actualiza un año lectivo existente
    """
    db_anio_lectivo = get_anio_lectivo(db, id_anio)
    if not db_anio_lectivo:
        return None
    
    update_data = anio_lectivo.dict(exclude_unset=True)
    
    # Si se está activando este año, desactivar cualquier otro
    if update_data.get("activo") == True:
        db.query(AnioLectivo).filter(AnioLectivo.id_anio != id_anio).filter(AnioLectivo.activo == True).update({"activo": False})
    
    for key, value in update_data.items():
        setattr(db_anio_lectivo, key, value)
    
    db.add(db_anio_lectivo)
    db.commit()
    db.refresh(db_anio_lectivo)
    return db_anio_lectivo


def delete_anio_lectivo(db: Session, id_anio: UUID) -> bool:
    """
    Elimina un año lectivo
    """
    db_anio_lectivo = get_anio_lectivo(db, id_anio)
    if not db_anio_lectivo:
        return False
    
    db.delete(db_anio_lectivo)
    db.commit()
    return True
