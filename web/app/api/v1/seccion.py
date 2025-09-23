from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.modules.secciones import crud, schemas
from app.modules.secciones.models import Seccion
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter()


@router.get("/obtener-secciones", response_model=List[schemas.Seccion])
def get_secciones(db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    from sqlalchemy.orm import aliased
    from app.modules.usuarios.models import Usuario
    
    ProfesorGuia = aliased(Usuario)
    
    query = db.query(
        Seccion,
        ProfesorGuia.nombre.label('profesor_guia_nombre')
    ).outerjoin(
        ProfesorGuia, Seccion.id_profesor_guia == ProfesorGuia.id_usuario
    )
    
    result = query.all()
    
    secciones = []
    for seccion, profesor_guia_nombre in result:
        seccion_dict = {
            "id_seccion": seccion.id_seccion,
            "nombre": seccion.nombre,
            "grado": seccion.grado,
            "id_profesor_guia": seccion.id_profesor_guia,
            "id_anio": seccion.id_anio,
            "profesor_guia_nombre": profesor_guia_nombre
        }
        secciones.append(seccion_dict)
    
    return secciones


@router.get("/obtener-secciones-por-anio/{id_anio}", response_model=List[schemas.Seccion])
def get_secciones_by_anio(id_anio: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    from sqlalchemy.orm import aliased
    from app.modules.usuarios.models import Usuario
    
    ProfesorGuia = aliased(Usuario)
    
    query = db.query(
        Seccion,
        ProfesorGuia.nombre.label('profesor_guia_nombre')
    ).outerjoin(
        ProfesorGuia, Seccion.id_profesor_guia == ProfesorGuia.id_usuario
    ).filter(Seccion.id_anio == id_anio)
    
    result = query.all()
    
    secciones = []
    for seccion, profesor_guia_nombre in result:
        seccion_dict = {
            "id_seccion": seccion.id_seccion,
            "nombre": seccion.nombre,
            "grado": seccion.grado,
            "id_profesor_guia": seccion.id_profesor_guia,
            "id_anio": seccion.id_anio,
            "profesor_guia_nombre": profesor_guia_nombre
        }
        secciones.append(seccion_dict)
    
    return secciones


@router.post("/crear-seccion", response_model=schemas.Seccion, status_code=status.HTTP_201_CREATED)
def create_seccion(seccion_in: schemas.SeccionCreate, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear secciones"
        )
    
    db_seccion = crud.get_seccion_by_nombre_grado_anio(
        db, 
        nombre=seccion_in.nombre, 
        grado=seccion_in.grado,
        id_anio=seccion_in.id_anio
    )
    if db_seccion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una sección con ese nombre y grado para el año lectivo seleccionado"
        )
    
    nueva_seccion = crud.create_seccion(db=db, seccion=seccion_in)
    
    profesor_guia_nombre = None
    if nueva_seccion.id_profesor_guia:
        from app.modules.usuarios.models import Usuario
        profesor_guia = db.query(Usuario).filter(Usuario.id_usuario == nueva_seccion.id_profesor_guia).first()
        if profesor_guia:
            profesor_guia_nombre = profesor_guia.nombre
    
    seccion_dict = {
        "id_seccion": nueva_seccion.id_seccion,
        "nombre": nueva_seccion.nombre,
        "grado": nueva_seccion.grado,
        "id_profesor_guia": nueva_seccion.id_profesor_guia,
        "id_anio": nueva_seccion.id_anio,
        "profesor_guia_nombre": profesor_guia_nombre
    }
    
    return seccion_dict


@router.get("/obtener-seccion/{id_seccion}", response_model=schemas.Seccion)
def get_seccion(id_seccion: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    db_seccion = crud.get_seccion(db, id_seccion=id_seccion)
    if db_seccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sección no encontrada"
        )
    
    profesor_guia_nombre = None
    if db_seccion.id_profesor_guia:
        from app.modules.usuarios.models import Usuario
        profesor_guia = db.query(Usuario).filter(Usuario.id_usuario == db_seccion.id_profesor_guia).first()
        if profesor_guia:
            profesor_guia_nombre = profesor_guia.nombre
    
    seccion_dict = {
        "id_seccion": db_seccion.id_seccion,
        "nombre": db_seccion.nombre,
        "grado": db_seccion.grado,
        "id_profesor_guia": db_seccion.id_profesor_guia,
        "id_anio": db_seccion.id_anio,
        "profesor_guia_nombre": profesor_guia_nombre
    }
    
    return seccion_dict


@router.put("/actualizar-seccion/{id_seccion}", response_model=schemas.Seccion)
def update_seccion(id_seccion: UUID, seccion_in: schemas.SeccionUpdate, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar secciones"
        )
    
    db_seccion = crud.get_seccion(db, id_seccion=id_seccion)
    if db_seccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sección no encontrada"
        )
    
    if (seccion_in.nombre or seccion_in.grado or seccion_in.id_anio) and not all([seccion_in.nombre, seccion_in.grado, seccion_in.id_anio]):
        nombre = seccion_in.nombre if seccion_in.nombre is not None else db_seccion.nombre
        grado = seccion_in.grado if seccion_in.grado is not None else db_seccion.grado
        id_anio = seccion_in.id_anio if seccion_in.id_anio is not None else db_seccion.id_anio
        
        existing_seccion = crud.get_seccion_by_nombre_grado_anio(db, nombre=nombre, grado=grado, id_anio=id_anio)
        if existing_seccion and existing_seccion.id_seccion != id_seccion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otra sección con ese nombre y grado para el año lectivo seleccionado"
            )
    
    # Actualizar la sección
    seccion_actualizada = crud.update_seccion(db=db, id_seccion=id_seccion, seccion_in=seccion_in)
    
    # Obtener el nombre del profesor guía si existe
    profesor_guia_nombre = None
    if seccion_actualizada.id_profesor_guia:
        from app.modules.usuarios.models import Usuario
        profesor_guia = db.query(Usuario).filter(Usuario.id_usuario == seccion_actualizada.id_profesor_guia).first()
        if profesor_guia:
            profesor_guia_nombre = profesor_guia.nombre
    
    # Crear un diccionario con los datos de la sección y el nombre del profesor guía
    seccion_dict = {
        "id_seccion": seccion_actualizada.id_seccion,
        "nombre": seccion_actualizada.nombre,
        "grado": seccion_actualizada.grado,
        "id_profesor_guia": seccion_actualizada.id_profesor_guia,
        "id_anio": seccion_actualizada.id_anio,
        "profesor_guia_nombre": profesor_guia_nombre
    }
    
    return seccion_dict


@router.delete("/eliminar-seccion/{id_seccion}", response_model=schemas.Seccion)
def delete_seccion(id_seccion: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    if current_user.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar secciones"
        )
    
    db_seccion = crud.delete_seccion(db, id_seccion=id_seccion)
    if db_seccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sección no encontrada"
        )
    return db_seccion


@router.get("/obtener-profesores-seccion/{id_seccion}", response_model=List[schemas.ProfesorBase])
def get_profesores_by_seccion(id_seccion: UUID, db: Session = Depends(get_db), current_user: UsuarioOut = Depends(get_current_user)):
    db_seccion = crud.get_seccion(db, id_seccion=id_seccion)
    if db_seccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sección no encontrada"
        )
    
    profesores = crud.get_profesores_by_seccion(db=db, id_seccion=id_seccion)
    return profesores
