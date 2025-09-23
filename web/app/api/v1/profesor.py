from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any
import uuid
from app.modules.profesores.schemas import (
    ProfesorBase, 
    ProfesorCreate,
    ProfesorUpdate,
    ProfesorCreated,
    ProfesorMateriasAsignacion, 
    ProfesorSeccionesAsignacion,
    ProfesorConMaterias,
    ProfesorConSecciones,
    ProfesorCompleto
)
from app.modules.profesores.crud import (
    obtener_profesores,
    obtener_profesor_por_id,
    obtener_materias_profesor,
    obtener_secciones_profesor,
    asignar_materias_profesor,
    asignar_secciones_profesor,
    obtener_profesor_completo,
    crear_profesor,
    eliminar_profesor,
    actualizar_profesor
)
from app.api.v1.deps import get_db, get_current_user
from app.modules.usuarios.models import Usuario
from app.core.email import send_welcome_email

router = APIRouter()


@router.post("/crear-profesor", response_model=ProfesorCreated)
async def create_profesor(profesor_data: ProfesorCreate,db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para crear profesores"
        )
    
    usuario_existente = db.query(Usuario).filter(Usuario.correo == profesor_data.correo).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo electrónico"
        )
    
    nuevo_profesor = crear_profesor(db, profesor_data.nombre, profesor_data.correo)
    
    try:
        await send_welcome_email(
            to_email=profesor_data.correo,
            nombre=profesor_data.nombre,
            password=nuevo_profesor['password']
        )
    except Exception as e:
        print(f"Error al enviar correo: {e}")
    
    return {
        "id_profesor": nuevo_profesor["id_profesor"],
        "nombre": nuevo_profesor["nombre"],
        "correo": nuevo_profesor["correo"]
    }


@router.get("/obtener-profesores")
def get_profesores(db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para obtener la lista de profesores"
        )
    
    try:
        profesores = obtener_profesores(db)
        return profesores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener profesores: {str(e)}"
        )


@router.get("/obtener-profesor/{id_profesor}", response_model=ProfesorCompleto)
def get_profesor(id_profesor: uuid.UUID, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion" and str(usuario_actual.id_usuario) != str(id_profesor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para obtener información de un profesor"
        )
    
    profesor = obtener_profesor_completo(db, id_profesor)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )
    
    return profesor


@router.put("/actualizar-profesor/{id_profesor}", response_model=ProfesorBase)
async def update_profesor(id_profesor: uuid.UUID, profesor_data: ProfesorUpdate,db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar un profesor"
        )
    
    usuario_existente = db.query(Usuario).filter(
        and_(
            Usuario.correo == profesor_data.correo,
            Usuario.id_usuario != id_profesor
        )
    ).first()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo electrónico"
        )
    
    profesor_actualizado = actualizar_profesor(
        db, 
        id_profesor, 
        profesor_data.nombre, 
        profesor_data.correo
    )
    
    if not profesor_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )
    
    return profesor_actualizado


@router.delete("/eliminar-profesor/{id_profesor}", response_model=dict)
async def delete_profesor(id_profesor: uuid.UUID,db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar un profesor"
        )
    
    resultado = eliminar_profesor(db, id_profesor)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )
    
    return {"mensaje": "Profesor eliminado correctamente"}


@router.get("/obtener-materias-profesor/{id_profesor}", response_model=List[Dict[str, Any]])
def get_materias_profesor(id_profesor: uuid.UUID, id_anio: uuid.UUID = None,db: Session = Depends(get_db), 
usuario_actual: Usuario = Depends(get_current_user)):

    if usuario_actual.rol != "direccion" and str(usuario_actual.id_usuario) != str(id_profesor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para ver las materias de este profesor"
        )
    
    profesor = obtener_profesor_por_id(db, id_profesor)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profesor no encontrado"
        )
    
    materias = obtener_materias_profesor(db, id_profesor, id_anio)
    return materias


@router.get("/obtener-secciones-profesor/{id_profesor}", response_model=List[Dict[str, Any]])
def get_secciones_profesor(id_profesor: uuid.UUID,db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion" and str(usuario_actual.id_usuario) != str(id_profesor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para ver las secciones de este profesor"
        )
    
    profesor = obtener_profesor_por_id(db, id_profesor)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profesor no encontrado"
        )
    
    secciones = obtener_secciones_profesor(db, id_profesor)
    return secciones


@router.post("/asignar-materias")
def post_asignar_materias(asignacion: ProfesorMateriasAsignacion,db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para asignar materias"
        )
    
    profesor = obtener_profesor_por_id(db, asignacion.id_profesor)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profesor no encontrado"
        )
    
    try:
        asignar_materias_profesor(db, asignacion.id_profesor, asignacion.id_materias, asignacion.id_anio)
        return {"mensaje": "Materias asignadas correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar materias: {str(e)}"
        )


@router.post("/asignar-secciones")
def post_asignar_secciones(asignacion: ProfesorSeccionesAsignacion,db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para asignar secciones"
        )
    
    profesor = obtener_profesor_por_id(db, asignacion.id_profesor)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profesor no encontrado"
        )
    
    try:
        asignar_secciones_profesor(db, asignacion.id_profesor, asignacion.id_secciones)
        return {"mensaje": "Secciones asignadas correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar secciones: {str(e)}"
        )
