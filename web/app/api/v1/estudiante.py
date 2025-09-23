from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.modules.estudiantes import crud, schemas
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter()


@router.get("/obtener-estudiantes", response_model=List[schemas.Estudiante])
def get_estudiantes(
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Obtener lista de estudiantes.
    Solo usuarios con rol 'direccion' o 'profesor' pueden acceder.
    """
    if current_user.rol not in ["direccion", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver la lista de estudiantes"
        )
    
    return crud.get_estudiantes(db, skip=skip, limit=limit)


@router.post("/crear-estudiante", response_model=schemas.EstudianteWithCredentials, status_code=status.HTTP_201_CREATED)
def create_estudiante(
    estudiante_in: schemas.EstudianteCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Crear un nuevo estudiante y generar automáticamente una cuenta de padre.
    Solo usuarios con rol 'direccion' pueden crear estudiantes.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear estudiantes"
        )
    
    # Verificar si ya existe un estudiante con esa cédula
    db_estudiante = crud.get_estudiante_by_cedula(db, cedula=estudiante_in.cedula)
    if db_estudiante:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un estudiante con esa cédula"
        )
    
    # Crear estudiante y cuenta de padre
    estudiante, correo_padre, contrasena_padre = crud.create_estudiante_with_padre(db, estudiante=estudiante_in)
    
    # Preparar respuesta
    response = {
        "id_estudiante": estudiante.id_estudiante,
        "cedula": estudiante.cedula,
        "nombre": estudiante.nombre,
        "primer_apellido": estudiante.primer_apellido,
        "segundo_apellido": estudiante.segundo_apellido,
        "id_padre": estudiante.id_padre,
        "correo_padre": correo_padre,
        "contrasena_padre": contrasena_padre
    }
    
    # Agregar información sobre la matrícula si se proporcionó una sección y año
    if estudiante_in.id_seccion and estudiante_in.id_anio:
        response["matriculado"] = True
        response["id_seccion"] = estudiante_in.id_seccion
        response["id_anio"] = estudiante_in.id_anio
    
    return response


@router.get("/obtener-estudiante/{id_estudiante}", response_model=schemas.Estudiante)
def get_estudiante(
    id_estudiante: UUID,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtener un estudiante por su ID.
    Solo usuarios con rol 'direccion' o 'profesor' pueden acceder.
    Los padres solo pueden ver a sus propios hijos.
    """
    # Verificar permisos
    if current_user.rol not in ["direccion", "profesor", "padre"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver estudiantes"
        )
    
    db_estudiante = crud.get_estudiante(db, id_estudiante=id_estudiante)
    if db_estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    # Si es un padre, solo puede ver a sus propios hijos
    if current_user.rol == "padre" and db_estudiante.id_padre != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este estudiante"
        )
    
    return db_estudiante


@router.put("/actualizar-estudiante/{id_estudiante}", response_model=schemas.Estudiante)
def update_estudiante(
    id_estudiante: UUID,
    estudiante_in: schemas.EstudianteUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Actualizar un estudiante.
    Solo usuarios con rol 'direccion' pueden actualizar estudiantes.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar estudiantes"
        )
    
    db_estudiante = crud.update_estudiante(db, id_estudiante=id_estudiante, estudiante=estudiante_in)
    if db_estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    return db_estudiante


@router.delete("/eliminar-estudiante/{id_estudiante}", response_model=schemas.Estudiante)
def delete_estudiante(
    id_estudiante: UUID,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Eliminar un estudiante.
    Solo usuarios con rol 'direccion' pueden eliminar estudiantes.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar estudiantes"
        )
    
    db_estudiante = crud.delete_estudiante(db, id_estudiante=id_estudiante)
    if db_estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    return db_estudiante
