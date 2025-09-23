from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user
from app.modules.padres import crud, schemas
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter()


@router.get("/mis-hijos", response_model=List[schemas.EstudianteHijo])
def get_hijos(
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtener la lista de estudiantes (hijos) asociados al padre autenticado.
    Solo usuarios con rol 'padre' pueden acceder a este endpoint.
    """
    if current_user.rol != "padre":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los padres pueden acceder a este recurso"
        )
    
    return crud.get_hijos_por_padre(db, id_padre=current_user.id_usuario)


@router.get("/notas-estudiante/{id_estudiante}", response_model=List[schemas.NotaEstudiante])
def get_notas_estudiante(
    id_estudiante: UUID,
    id_anio: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtener las notas de un estudiante específico.
    Solo el padre del estudiante puede acceder a sus notas.
    """
    if current_user.rol != "padre":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los padres pueden acceder a este recurso"
        )
    
    # Verificar que el estudiante pertenece al padre autenticado
    estudiante = crud.get_hijo_por_id(db, id_estudiante=id_estudiante, id_padre=current_user.id_usuario)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o no tiene permisos para ver sus notas"
        )
    
    return crud.get_notas_estudiante(db, id_estudiante=id_estudiante, id_anio=id_anio)


@router.get("/asistencias-estudiante/{id_estudiante}", response_model=List[schemas.AsistenciaEstudiante])
def get_asistencias_estudiante(
    id_estudiante: UUID,
    id_anio: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtener las asistencias de un estudiante específico.
    Solo el padre del estudiante puede acceder a sus asistencias.
    """
    if current_user.rol != "padre":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los padres pueden acceder a este recurso"
        )
    
    # Verificar que el estudiante pertenece al padre autenticado
    estudiante = crud.get_hijo_por_id(db, id_estudiante=id_estudiante, id_padre=current_user.id_usuario)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o no tiene permisos para ver sus asistencias"
        )
    
    return crud.get_asistencias_estudiante(db, id_estudiante=id_estudiante, id_anio=id_anio)


# Endpoints para administración de padres (solo accesibles para dirección)

@router.get("/obtener-padres", response_model=List[schemas.PadreOutWithHijos])
def get_padres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtener lista de todos los padres con sus hijos asociados.
    Solo usuarios con rol 'direccion' pueden acceder a este endpoint.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo la dirección puede acceder a este recurso"
        )
    
    return crud.get_padres_with_hijos(db, skip=skip, limit=limit)


@router.get("/obtener-padre/{id_padre}", response_model=schemas.PadreOutWithHijos)
def get_padre(
    id_padre: UUID,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Obtener información detallada de un padre específico, incluyendo sus hijos.
    Solo usuarios con rol 'direccion' pueden acceder a este endpoint.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo la dirección puede acceder a este recurso"
        )
    
    padre = crud.get_padre_por_id(db, id_padre=id_padre)
    if not padre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Padre no encontrado"
        )
    
    # Obtener los hijos del padre
    hijos = crud.get_hijos_por_padre(db, id_padre=id_padre)
    
    # Crear el objeto de respuesta
    response = schemas.PadreOutWithHijos(
        id_usuario=padre.id_usuario,
        nombre=padre.nombre,
        correo=padre.correo,
        activo=padre.activo,
        foto=padre.foto,
        rol=padre.rol,
        hijos=[schemas.EstudianteHijo(id_estudiante=hijo.id_estudiante, nombre=hijo.nombre) for hijo in hijos]
    )
    
    return response


@router.put("/actualizar-padre/{id_padre}", response_model=schemas.PadreOut)
def update_padre(
    id_padre: UUID,
    padre_data: schemas.PadreUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Actualizar información de un padre específico.
    Solo usuarios con rol 'direccion' pueden acceder a este endpoint.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo la dirección puede acceder a este recurso"
        )
    
    padre, success, message = crud.actualizar_padre(
        db, 
        id_padre=id_padre, 
        nombre=padre_data.nombre, 
        correo=padre_data.correo, 
        activo=padre_data.activo, 
        foto=padre_data.foto
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return padre


@router.delete("/eliminar-padre/{id_padre}", response_model=schemas.MensajeResponse)
def delete_padre(
    id_padre: UUID,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Eliminar un padre específico y desvincular sus estudiantes asociados.
    Solo usuarios con rol 'direccion' pueden acceder a este endpoint.
    """
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo la dirección puede acceder a este recurso"
        )
    
    success, message = crud.eliminar_padre(db, id_padre=id_padre)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"mensaje": message}


@router.post("/cambiar-contrasena", response_model=schemas.MensajeResponse)
def cambiar_contrasena(
    datos: schemas.CambioContrasenaRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioOut = Depends(get_current_user)
):
    """
    Cambiar la contraseña del padre autenticado.
    Solo usuarios con rol 'padre' pueden acceder a este endpoint.
    """
    if current_user.rol != "padre":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los padres pueden cambiar su contraseña a través de este endpoint"
        )
    
    success, message = crud.cambiar_contrasena_padre(
        db, 
        id_padre=current_user.id_usuario, 
        contrasena_actual=datos.contrasena_actual, 
        nueva_contrasena=datos.nueva_contrasena
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"mensaje": message}
