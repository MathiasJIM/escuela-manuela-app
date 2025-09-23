from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.modules.documentos import crud, schemas
from app.modules.usuarios.models import Usuario

router = APIRouter()


@router.post("/subir-documento", response_model=schemas.DocumentoOut)
async def crear_documento(
    documento: schemas.DocumentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo documento con enlace.
    
    - Solo usuarios autenticados pueden crear documentos.
    - Se guarda el enlace al documento externo (Google Drive, OneDrive, etc.).
    """
    # Verificar que el usuario tenga permisos (dirección o profesores)
    if current_user.rol not in ["direccion", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear documentos"
        )
    
    return crud.create_documento(
        db=db, 
        documento=documento,
        id_usuario=current_user.id_usuario
    )


@router.get("/todos-documentos", response_model=List[schemas.DocumentoOut])
def obtener_documentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener lista de documentos según el rol del usuario.
    
    - Dirección: puede ver todos los documentos
    - Profesores: puede ver documentos para profesores y todos
    - Padres: puede ver documentos para padres y todos
    """
    # Determinar qué documentos puede ver según su rol
    if current_user.rol == "direccion":
        # Dirección puede ver todos los documentos
        return crud.get_documentos(db, skip=skip, limit=limit)
    else:
        # Otros roles solo ven los documentos dirigidos a su rol o a todos
        return crud.get_documentos(
            db, 
            skip=skip, 
            limit=limit, 
            destinatario=current_user.rol
        )


@router.get("/obtener-documento/{id_documento}", response_model=schemas.DocumentoOut)
def obtener_documento(
    id_documento: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener un documento específico por su ID.
    
    - El usuario debe tener permiso para ver el documento según su rol
    """
    documento = crud.get_documento(db, id_documento=id_documento)
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol != "direccion" and documento.destinatario not in [current_user.rol, "todos"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este documento"
        )
    
    return documento


@router.put("/actualizar-documento/{id_documento}", response_model=schemas.DocumentoOut)
def actualizar_documento(
    id_documento: UUID,
    documento_update: schemas.DocumentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar un documento existente.
    
    - Solo dirección o el usuario que subió el documento pueden actualizarlo
    """
    db_documento = crud.get_documento(db, id_documento=id_documento)
    if not db_documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol != "direccion" and db_documento.subido_por != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar este documento"
        )
    
    return crud.update_documento(db, db_documento=db_documento, documento=documento_update)


@router.delete("/eliminar-documento/{id_documento}", response_model=schemas.DocumentoOut)
def eliminar_documento(
    id_documento: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar un documento.
    
    - Solo dirección o el usuario que subió el documento pueden eliminarlo
    """
    db_documento = crud.get_documento(db, id_documento=id_documento)
    if not db_documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol != "direccion" and db_documento.subido_por != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar este documento"
        )
    
    return crud.delete_documento(db, db_documento=db_documento)


@router.get("/obtener-enlace-documento/{id_documento}")
def obtener_enlace_documento(
    id_documento: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    documento = crud.get_documento(db, id_documento)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Verificar permisos
    if current_user.rol != "direccion" and documento.destinatario not in [current_user.rol, "todos"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver este documento"
        )
    
    return {"enlace": documento.archivo}
