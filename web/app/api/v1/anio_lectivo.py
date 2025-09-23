from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.modules.anio_lectivo import crud, schemas
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter()


@router.get("/obtener-anios-lectivos", response_model=List[schemas.AnioLectivo])
def obtener_anios_lectivos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtiene todos los años lectivos.
    
    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a devolver
    
    Requiere autenticación.
    """
    # Verificar que el usuario tenga permisos (dirección o profesor)
    if current_user.rol not in ["direccion", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    anios_lectivos = crud.get_anios_lectivos(db, skip=skip, limit=limit)
    return anios_lectivos


@router.get("/obtener-anio-lectivo/{id_anio}", response_model=schemas.AnioLectivo)
def obtener_anio_lectivo(
    id_anio: UUID, 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtiene un año lectivo por su ID.
    
    - **id_anio**: ID del año lectivo a obtener
    
    Requiere autenticación.
    """
    # Verificar que el usuario tenga permisos (dirección o profesor)
    if current_user.rol not in ["direccion", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    anio_lectivo = crud.get_anio_lectivo(db, id_anio=id_anio)
    if anio_lectivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año lectivo no encontrado"
        )
    return anio_lectivo


@router.get("/obtener-anio-lectivo-activo", response_model=schemas.AnioLectivo)
def obtener_anio_lectivo_activo(
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtiene el año lectivo activo.
    
    Requiere autenticación.
    """
    # Verificar que el usuario tenga permisos (dirección, profesor o padre)
    if current_user.rol not in ["direccion", "profesor", "padre"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    anio_lectivo = crud.get_anio_lectivo_activo(db)
    if anio_lectivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay año lectivo activo"
        )
    return anio_lectivo


@router.post("/crear-anio-lectivo", response_model=schemas.AnioLectivo)
def crear_anio_lectivo(
    anio_lectivo: schemas.AnioLectivoCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Crea un nuevo año lectivo.
    
    - **anio_lectivo**: Datos del año lectivo a crear
    
    Requiere autenticación y rol de dirección.
    """
    # Verificar que el usuario tenga permisos (solo dirección)
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    # Verificar que no exista un año lectivo con el mismo nombre
    db_anio_lectivo = crud.get_anio_lectivo_by_nombre(db, nombre=anio_lectivo.nombre)
    if db_anio_lectivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un año lectivo con ese nombre"
        )
    
    # Verificar que la fecha de inicio sea anterior a la fecha de fin
    if anio_lectivo.fecha_inicio >= anio_lectivo.fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio debe ser anterior a la fecha de fin"
        )
    
    return crud.create_anio_lectivo(db=db, anio_lectivo=anio_lectivo)


@router.put("/actualizar-anio-lectivo/{id_anio}", response_model=schemas.AnioLectivo)
def actualizar_anio_lectivo(
    id_anio: UUID, 
    anio_lectivo: schemas.AnioLectivoUpdate, 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Actualiza un año lectivo existente.
    
    - **id_anio**: ID del año lectivo a actualizar
    - **anio_lectivo**: Datos actualizados del año lectivo
    
    Requiere autenticación y rol de dirección.
    """
    # Verificar que el usuario tenga permisos (solo dirección)
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    # Verificar que el año lectivo exista
    db_anio_lectivo = crud.get_anio_lectivo(db, id_anio=id_anio)
    if db_anio_lectivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año lectivo no encontrado"
        )
    
    # Si se está actualizando el nombre, verificar que no exista otro con ese nombre
    if anio_lectivo.nombre is not None and anio_lectivo.nombre != db_anio_lectivo.nombre:
        db_anio_nombre = crud.get_anio_lectivo_by_nombre(db, nombre=anio_lectivo.nombre)
        if db_anio_nombre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un año lectivo con ese nombre"
            )
    
    # Verificar fechas si se están actualizando
    fecha_inicio = anio_lectivo.fecha_inicio or db_anio_lectivo.fecha_inicio
    fecha_fin = anio_lectivo.fecha_fin or db_anio_lectivo.fecha_fin
    
    if fecha_inicio >= fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio debe ser anterior a la fecha de fin"
        )
    
    updated_anio = crud.update_anio_lectivo(db=db, id_anio=id_anio, anio_lectivo=anio_lectivo)
    if updated_anio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año lectivo no encontrado"
        )
    return updated_anio


@router.delete("/eliminar-anio-lectivo/{id_anio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_anio_lectivo(
    id_anio: UUID, 
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Elimina un año lectivo.
    
    - **id_anio**: ID del año lectivo a eliminar
    
    Requiere autenticación y rol de dirección.
    """
    # Verificar que el usuario tenga permisos (solo dirección)
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    # Verificar que el año lectivo exista
    db_anio_lectivo = crud.get_anio_lectivo(db, id_anio=id_anio)
    if db_anio_lectivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año lectivo no encontrado"
        )
    
    # No permitir eliminar un año lectivo activo
    if db_anio_lectivo.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un año lectivo activo"
        )
    
    success = crud.delete_anio_lectivo(db=db, id_anio=id_anio)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el año lectivo"
        )
    return None
