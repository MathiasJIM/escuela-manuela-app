from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.modules.materias import crud, schemas
from app.modules.materias.models import Materia
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter()


@router.get("/obtener-materias", response_model=List[schemas.Materia])
def get_materias(db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    materias = db.query(Materia).all()
    return materias


@router.post("/crear-materia", response_model=schemas.Materia, status_code=status.HTTP_201_CREATED)
def create_materia(materia_in: schemas.MateriaCreate, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear materias"
        )
    
    db_materia = crud.get_materia_by_nombre(db, nombre=materia_in.nombre)
    if db_materia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una materia con ese nombre"
        )
    
    return crud.create_materia(db=db, materia=materia_in)


@router.get("/obtener-materia/{id_materia}", response_model=schemas.Materia)
def get_materia(id_materia: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    db_materia = crud.get_materia(db, id_materia=id_materia)
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    return db_materia


@router.put("/actualizar-materia/{id_materia}", response_model=schemas.Materia)
def update_materia(
    id_materia: UUID,
    materia_in: schemas.MateriaUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar materias"
        )
    
    db_materia = crud.get_materia(db, id_materia=id_materia)
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    existing_materia = crud.get_materia_by_nombre(db, nombre=materia_in.nombre)
    if existing_materia and existing_materia.id_materia != id_materia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otra materia con ese nombre"
        )
    
    return crud.update_materia(db=db, id_materia=id_materia, materia_in=materia_in)


@router.delete("/eliminar-materia/{id_materia}", response_model=schemas.Materia)
def delete_materia(id_materia: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar materias"
        )
    
    db_materia = crud.delete_materia(db, id_materia=id_materia)
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    return db_materia


@router.get("/obtener-profesores-materia/{id_materia}", response_model=List[schemas.ProfesorBase])
def get_profesores_by_materia(id_materia: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    db_materia = crud.get_materia(db, id_materia=id_materia)
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    profesores = crud.get_profesores_by_materia(db=db, id_materia=id_materia)
    return profesores
