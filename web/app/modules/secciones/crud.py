from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, join
from fastapi.encoders import jsonable_encoder

from app.modules.secciones.models import Seccion
from app.modules.secciones.models_profesor_seccion import ProfesorSeccion
from app.modules.secciones.schemas import SeccionCreate, SeccionUpdate
from app.modules.usuarios.models import Usuario, Profesor


def get_seccion(db: Session, id_seccion: UUID) -> Optional[Seccion]:
    return db.query(Seccion).filter(Seccion.id_seccion == id_seccion).first()


def get_seccion_by_nombre_grado_anio(db: Session, nombre: str, grado: str, id_anio: UUID) -> Optional[Seccion]:
    return db.query(Seccion).filter(
        Seccion.nombre == nombre,
        Seccion.grado == grado,
        Seccion.id_anio == id_anio
    ).first()


def get_secciones(db: Session, skip: int = 0, limit: int = 100) -> List[Seccion]:
    return db.query(Seccion).offset(skip).limit(limit).all()


def get_secciones_by_anio(db: Session, id_anio: UUID, skip: int = 0, limit: int = 100) -> List[Seccion]:
    return db.query(Seccion).filter(Seccion.id_anio == id_anio).offset(skip).limit(limit).all()


def create_seccion(db: Session, seccion: SeccionCreate) -> Seccion:
    db_seccion = Seccion(
        nombre=seccion.nombre,
        grado=seccion.grado,
        id_profesor_guia=seccion.id_profesor_guia,
        id_anio=seccion.id_anio
    )
    
    db.add(db_seccion)
    db.commit()
    db.refresh(db_seccion)
    
    return db_seccion


def update_seccion(db: Session, id_seccion: UUID, seccion_in: SeccionUpdate) -> Optional[Seccion]:
    db_seccion = get_seccion(db, id_seccion)
    if not db_seccion:
        return None
    
    update_data = seccion_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_seccion, field, value)
    
    db.add(db_seccion)
    db.commit()
    db.refresh(db_seccion)
    
    return db_seccion


def delete_seccion(db: Session, id_seccion: UUID) -> Optional[Seccion]:
    db_seccion = get_seccion(db, id_seccion=id_seccion)
    if db_seccion is None:
        return None
        
    db.delete(db_seccion)
    db.commit()
    
    return db_seccion


def get_profesores_by_seccion(db: Session, id_seccion: UUID) -> List[Dict[str, Any]]:
    db_seccion = get_seccion(db, id_seccion=id_seccion)
    if db_seccion is None:
        return []
    
    query = (
        db.query(
            Usuario.id_usuario.label('id_profesor'),
            Usuario.nombre,
            Usuario.correo
        )
        .join(Profesor, Profesor.id_profesor == Usuario.id_usuario)
        .join(ProfesorSeccion, ProfesorSeccion.id_profesor == Profesor.id_profesor)
        .filter(ProfesorSeccion.id_seccion == id_seccion)
    )
    
    profesores = []
    for row in query.all():
        profesor = {
            "id_profesor": row.id_profesor,
            "nombre": row.nombre,
            "correo": row.correo
        }
        profesores.append(profesor)
    
    return profesores
