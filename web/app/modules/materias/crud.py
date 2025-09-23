from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, join
from fastapi.encoders import jsonable_encoder

from app.modules.materias.models import Materia
from app.modules.materias.models_profesor_materia import ProfesorMateria
from app.modules.materias.schemas import MateriaCreate, MateriaUpdate
from app.modules.usuarios.models import Usuario, Profesor


def get_materia(db: Session, id_materia: UUID) -> Optional[Materia]:
    return db.query(Materia).filter(Materia.id_materia == id_materia).first()


def get_materia_by_nombre(db: Session, nombre: str) -> Optional[Materia]:
    return db.query(Materia).filter(Materia.nombre == nombre).first()


def get_materias(db: Session, skip: int = 0, limit: int = 100) -> List[Materia]:
    return db.query(Materia).offset(skip).limit(limit).all()


def create_materia(db: Session, materia: MateriaCreate) -> Materia:
    db_materia = Materia(
        nombre=materia.nombre
    )
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia


def update_materia(db: Session, id_materia: UUID, materia_in: MateriaUpdate) -> Optional[Materia]:
    db_materia = get_materia(db, id_materia)
    if not db_materia:
        return None
    
    update_data = materia_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_materia, field, value)
    
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia


def delete_materia(db: Session, id_materia: UUID) -> Optional[Materia]:
    db_materia = get_materia(db, id_materia=id_materia)
    if db_materia is None:
        return None
        
    db.delete(db_materia)
    db.commit()
    
    return db_materia


def get_profesores_by_materia(db: Session, id_materia: UUID) -> List[Dict[str, Any]]:
    db_materia = get_materia(db, id_materia=id_materia)
    if db_materia is None:
        return []
    
    query = (
        db.query(
            Usuario.id_usuario.label('id_profesor'),
            Usuario.nombre,
            Usuario.correo
        )
        .join(Profesor, Profesor.id_profesor == Usuario.id_usuario)
        .join(ProfesorMateria, ProfesorMateria.id_profesor == Profesor.id_profesor)
        .filter(ProfesorMateria.id_materia == id_materia)
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
