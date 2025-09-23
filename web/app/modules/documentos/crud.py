from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.modules.documentos.models import Documento
from app.modules.documentos.schemas import DocumentoCreate, DocumentoUpdate


def get_documento(db: Session, id_documento: UUID) -> Optional[Documento]:
    """
    Obtener un documento por su ID
    """
    return db.query(Documento).filter(Documento.id_documento == id_documento).first()


def get_documentos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    destinatario: Optional[str] = None
) -> List[Documento]:
    """
    Obtener lista de documentos con filtro opcional por destinatario
    """
    query = db.query(Documento)
    
    if destinatario:
        # Si se especifica un destinatario, filtramos por ese destinatario o 'todos'
        query = query.filter(
            (Documento.destinatario == destinatario) | 
            (Documento.destinatario == 'todos')
        )
    
    return query.order_by(Documento.fecha_subida.desc()).offset(skip).limit(limit).all()


def create_documento(
    db: Session, 
    documento: DocumentoCreate, 
    id_usuario: UUID
) -> Documento:
    """
    Crear un nuevo documento con enlace
    """
    db_documento = Documento(
        titulo=documento.titulo,
        descripcion=documento.descripcion,
        tipo=documento.tipo,
        archivo=documento.archivo,
        subido_por=id_usuario,
        destinatario=documento.destinatario
    )
    db.add(db_documento)
    db.commit()
    db.refresh(db_documento)
    return db_documento


def update_documento(
    db: Session, 
    db_documento: Documento, 
    documento: DocumentoUpdate
) -> Documento:
    """
    Actualizar un documento existente
    """
    obj_data = jsonable_encoder(db_documento)
    update_data = documento.dict(exclude_unset=True)
    
    for field in obj_data:
        if field in update_data:
            setattr(db_documento, field, update_data[field])
    
    db.add(db_documento)
    db.commit()
    db.refresh(db_documento)
    return db_documento


def delete_documento(db: Session, db_documento: Documento) -> Documento:
    """
    Eliminar un documento
    """
    db.delete(db_documento)
    db.commit()
    return db_documento
