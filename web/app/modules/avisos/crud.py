from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.avisos import schemas
from app.modules.avisos.models import Aviso


def get_aviso(db: Session, id_aviso: UUID) -> Optional[Aviso]:
    return db.query(Aviso).filter(Aviso.id_aviso == id_aviso).first()


def get_avisos(db: Session, skip: int = 0, limit: int = 100) -> List[Aviso]:
    return db.query(Aviso).offset(skip).limit(limit).all()


def get_avisos_por_destinatario(db: Session, destinatario: str, skip: int = 0, limit: int = 100) -> List[Aviso]:
    return db.query(Aviso).filter(Aviso.destinatario == destinatario).offset(skip).limit(limit).all()


def create_aviso(db: Session, aviso: schemas.AvisoCreate) -> Aviso:
    db_aviso = Aviso(**aviso.dict())
    db.add(db_aviso)
    db.commit()
    db.refresh(db_aviso)
    return db_aviso


def update_aviso(db: Session, id_aviso: UUID, aviso: schemas.AvisoUpdate) -> Optional[Aviso]:
    db_aviso = get_aviso(db, id_aviso)
    if db_aviso:
        update_data = aviso.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_aviso, key, value)
        db.commit()
        db.refresh(db_aviso)
    return db_aviso


def delete_aviso(db: Session, id_aviso: UUID) -> bool:
    db_aviso = get_aviso(db, id_aviso)
    if db_aviso:
        db.delete(db_aviso)
        db.commit()
        return True
    return False
